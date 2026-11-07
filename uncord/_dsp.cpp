//audio maths for voice: 16 bit pcm gain, mixing, levels and the call sounds
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <dlfcn.h>

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <utility>
#include <vector>

namespace {

//holds a read only view of anything with the buffer protocol and lets it go on scope exit
class Pcm {
public:
    explicit Pcm(PyObject *obj) {
        ok = PyObject_GetBuffer(obj, &view, PyBUF_SIMPLE) == 0;
    }
    ~Pcm() {
        if (ok)
            PyBuffer_Release(&view);
    }
    Pcm(const Pcm &) = delete;
    Pcm &operator=(const Pcm &) = delete;

    bool ok = false;
    Py_buffer view{};

    Py_ssize_t samples() const { return view.len / 2; }

    int16_t at(Py_ssize_t i) const {
        int16_t s;
        std::memcpy(&s, static_cast<const char *>(view.buf) + i * 2, 2);
        return s;
    }
};

inline int16_t clip(double v) {
    return static_cast<int16_t>(std::floor(std::clamp(v, -32768.0, 32767.0)));
}

inline int16_t clip(int32_t v) {
    return static_cast<int16_t>(std::clamp<int32_t>(v, -32768, 32767));
}

//builds the bytes result in place so there is no extra copy
template <typename Fill>
PyObject *makeBytes(Py_ssize_t samples, Fill fill) {
    PyObject *out = PyBytes_FromStringAndSize(nullptr, samples * 2);
    if (!out)
        return nullptr;
    auto *dst = reinterpret_cast<int16_t *>(PyBytes_AS_STRING(out));
    fill(dst);
    return out;
}

PyObject *gain(PyObject *, PyObject *args) {
    PyObject *obj;
    double g;
    if (!PyArg_ParseTuple(args, "Od", &obj, &g))
        return nullptr;
    Pcm in(obj);
    if (!in.ok)
        return nullptr;
    Py_ssize_t n = in.samples();
    return makeBytes(n, [&](int16_t *dst) {
        for (Py_ssize_t i = 0; i < n; i++)
            dst[i] = clip(in.at(i) * g);
    });
}

//sums any number of equal length frames then applies the volume, clipping once at the end
PyObject *mix(PyObject *, PyObject *args) {
    PyObject *frames;
    double volume = 1.0;
    if (!PyArg_ParseTuple(args, "O|d", &frames, &volume))
        return nullptr;
    PyObject *seq = PySequence_Fast(frames, "mix wants a list of frames");
    if (!seq)
        return nullptr;
    Py_ssize_t count = PySequence_Fast_GET_SIZE(seq);
    std::vector<int32_t> acc;
    for (Py_ssize_t f = 0; f < count; f++) {
        Pcm in(PySequence_Fast_GET_ITEM(seq, f));
        if (!in.ok) {
            Py_DECREF(seq);
            return nullptr;
        }
        if (acc.size() < static_cast<size_t>(in.samples()))
            acc.resize(in.samples(), 0);
        for (Py_ssize_t i = 0; i < in.samples(); i++)
            acc[i] += in.at(i);
    }
    Py_DECREF(seq);
    return makeBytes(static_cast<Py_ssize_t>(acc.size()), [&](int16_t *dst) {
        for (size_t i = 0; i < acc.size(); i++)
            dst[i] = volume == 1.0 ? clip(acc[i]) : clip(acc[i] * volume);
    });
}

PyObject *rms(PyObject *, PyObject *obj) {
    Pcm in(obj);
    if (!in.ok)
        return nullptr;
    Py_ssize_t n = in.samples();
    if (n == 0)
        return PyLong_FromLong(0);
    double sum = 0;
    for (Py_ssize_t i = 0; i < n; i++) {
        double s = in.at(i);
        sum += s * s;
    }
    return PyLong_FromLong(static_cast<long>(std::sqrt(sum / n)));
}

PyObject *peak(PyObject *, PyObject *obj) {
    Pcm in(obj);
    if (!in.ok)
        return nullptr;
    int32_t best = 0;
    for (Py_ssize_t i = 0; i < in.samples(); i++)
        best = std::max(best, std::abs(static_cast<int32_t>(in.at(i))));
    return PyLong_FromLong(best);
}

//one level per chunk for voice message waveforms
PyObject *levels(PyObject *, PyObject *args) {
    PyObject *obj;
    Py_ssize_t chunk;
    if (!PyArg_ParseTuple(args, "On", &obj, &chunk))
        return nullptr;
    if (chunk < 2) {
        PyErr_SetString(PyExc_ValueError, "chunk must be at least 2 bytes");
        return nullptr;
    }
    Pcm in(obj);
    if (!in.ok)
        return nullptr;
    Py_ssize_t per = chunk / 2, n = in.samples();
    PyObject *out = PyList_New(0);
    if (!out)
        return nullptr;
    for (Py_ssize_t start = 0; start < n; start += per) {
        Py_ssize_t end = std::min(n, start + per);
        double sum = 0;
        for (Py_ssize_t i = start; i < end; i++) {
            double s = in.at(i);
            sum += s * s;
        }
        PyObject *v = PyLong_FromLong(static_cast<long>(std::sqrt(sum / (end - start))));
        if (!v || PyList_Append(out, v) < 0) {
            Py_XDECREF(v);
            Py_DECREF(out);
            return nullptr;
        }
        Py_DECREF(v);
    }
    return out;
}

//stereo sine notes with a short attack and release, [(freq, secs), ...]
PyObject *tones(PyObject *, PyObject *args) {
    PyObject *notes;
    int rate;
    double volume;
    if (!PyArg_ParseTuple(args, "Oid", &notes, &rate, &volume))
        return nullptr;
    PyObject *seq = PySequence_Fast(notes, "tones wants a list of (freq, secs)");
    if (!seq)
        return nullptr;
    std::vector<std::pair<double, double>> parts;
    for (Py_ssize_t k = 0; k < PySequence_Fast_GET_SIZE(seq); k++) {
        double freq, secs;
        if (!PyArg_ParseTuple(PySequence_Fast_GET_ITEM(seq, k), "dd", &freq, &secs)) {
            Py_DECREF(seq);
            return nullptr;
        }
        parts.emplace_back(freq, secs);
    }
    Py_DECREF(seq);
    std::vector<int16_t> pcm;
    const double tau = 2 * M_PI;
    const long attack = static_cast<long>(rate * 0.005), release = static_cast<long>(rate * 0.03);
    for (auto [freq, secs] : parts) {
        long n = static_cast<long>(rate * secs);
        for (long i = 0; i < n; i++) {
            double env = std::min({1.0, attack ? double(i) / attack : 1.0, release ? double(n - i) / release : 1.0});
            double t = double(i) / rate;
            double v = (std::sin(tau * freq * t) + 0.25 * std::sin(2 * tau * freq * t)) / 1.25;
            int16_t s = clip(32767 * volume * env * v);
            pcm.push_back(s);
            pcm.push_back(s);
        }
    }
    pcm.resize(pcm.size() + static_cast<size_t>(rate / 50) * 2, 0);
    return makeBytes(static_cast<Py_ssize_t>(pcm.size()), [&](int16_t *dst) {
        std::copy(pcm.begin(), pcm.end(), dst);
    });
}

//opus decoding straight from libopus, the ctypes wrapper spends more time converting than decoding
struct OpusApi {
    void *(*create)(int32_t, int, int *) = nullptr;
    int (*decode)(void *, const unsigned char *, int32_t, int16_t *, int, int) = nullptr;
    int (*ctl)(void *, int, ...) = nullptr;
    void (*destroy)(void *) = nullptr;
    int (*nbFrames)(const unsigned char *, int32_t) = nullptr;
    int (*samplesPerFrame)(const unsigned char *, int32_t) = nullptr;
};

OpusApi opusApi;
constexpr int OPUS_RATE = 48000, OPUS_CHANNELS = 2, OPUS_FRAME = 960, OPUS_MAX_FRAME = 5760;
constexpr int CTL_LAST_PACKET_DURATION = 4039;
const char *DECODER_NAME = "uncord.opus.decoder";

template <typename F>
bool bind(void *lib, const char *name, F &out) {
    out = reinterpret_cast<F>(dlsym(lib, name));
    return out != nullptr;
}

PyObject *opusLoad(PyObject *, PyObject *args) {
    const char *path;
    if (!PyArg_ParseTuple(args, "s", &path))
        return nullptr;
    if (opusApi.decode)
        Py_RETURN_TRUE;
    void *lib = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    if (!lib)
        Py_RETURN_FALSE;
    OpusApi api;
    if (!bind(lib, "opus_decoder_create", api.create) || !bind(lib, "opus_decode", api.decode) ||
        !bind(lib, "opus_decoder_ctl", api.ctl) || !bind(lib, "opus_decoder_destroy", api.destroy) ||
        !bind(lib, "opus_packet_get_nb_frames", api.nbFrames) ||
        !bind(lib, "opus_packet_get_samples_per_frame", api.samplesPerFrame)) {
        dlclose(lib);
        Py_RETURN_FALSE;
    }
    opusApi = api;
    Py_RETURN_TRUE;
}

void destroyDecoder(PyObject *capsule) {
    void *st = PyCapsule_GetPointer(capsule, DECODER_NAME);
    if (st && opusApi.destroy)
        opusApi.destroy(st);
}

PyObject *opusDecoder(PyObject *, PyObject *) {
    if (!opusApi.create) {
        PyErr_SetString(PyExc_RuntimeError, "libopus is not loaded");
        return nullptr;
    }
    int err = 0;
    void *st = opusApi.create(OPUS_RATE, OPUS_CHANNELS, &err);
    if (!st || err != 0) {
        PyErr_Format(PyExc_RuntimeError, "opus_decoder_create failed (%d)", err);
        return nullptr;
    }
    return PyCapsule_New(st, DECODER_NAME, destroyDecoder);
}

//same frame size rules as discord.py: the packet says how long it is, a lost packet repeats the last length
PyObject *opusDecode(PyObject *, PyObject *args) {
    PyObject *capsule, *data;
    int fec = 0;
    if (!PyArg_ParseTuple(args, "OO|p", &capsule, &data, &fec))
        return nullptr;
    void *st = PyCapsule_GetPointer(capsule, DECODER_NAME);
    if (!st)
        return nullptr;
    const unsigned char *buf = nullptr;
    Py_ssize_t len = 0;
    Py_buffer view{};
    bool held = false;
    int frameSize = OPUS_FRAME;
    if (data == Py_None) {
        if (fec) {
            PyErr_SetString(PyExc_TypeError, "fec needs packet data");
            return nullptr;
        }
        int32_t last = 0;
        opusApi.ctl(st, CTL_LAST_PACKET_DURATION, &last);
        frameSize = last > 0 ? last : OPUS_FRAME;
    } else {
        if (PyObject_GetBuffer(data, &view, PyBUF_SIMPLE) != 0)
            return nullptr;
        held = true;
        buf = static_cast<const unsigned char *>(view.buf);
        len = view.len;
        int frames = opusApi.nbFrames(buf, static_cast<int32_t>(len));
        int spf = opusApi.samplesPerFrame(buf, OPUS_RATE);
        if (frames < 0 || spf <= 0) {
            PyBuffer_Release(&view);
            PyErr_Format(PyExc_ValueError, "bad opus packet (%d)", frames);
            return nullptr;
        }
        frameSize = frames * spf;
    }
    frameSize = std::clamp(frameSize, 1, OPUS_MAX_FRAME);
    int16_t pcm[OPUS_MAX_FRAME * OPUS_CHANNELS];
    int got;
    Py_BEGIN_ALLOW_THREADS
    got = opusApi.decode(st, buf, static_cast<int32_t>(len), pcm, frameSize, fec);
    Py_END_ALLOW_THREADS
    if (held)
        PyBuffer_Release(&view);
    if (got < 0) {
        PyErr_Format(PyExc_ValueError, "opus_decode failed (%d)", got);
        return nullptr;
    }
    return PyBytes_FromStringAndSize(reinterpret_cast<const char *>(pcm),
                                     static_cast<Py_ssize_t>(got) * OPUS_CHANNELS * 2);
}

PyMethodDef methods[] = {
    {"gain", gain, METH_VARARGS, nullptr},
    {"mix", mix, METH_VARARGS, nullptr},
    {"rms", rms, METH_O, nullptr},
    {"peak", peak, METH_O, nullptr},
    {"levels", levels, METH_VARARGS, nullptr},
    {"tones", tones, METH_VARARGS, nullptr},
    {"opusLoad", opusLoad, METH_VARARGS, nullptr},
    {"opusDecoder", opusDecoder, METH_NOARGS, nullptr},
    {"opusDecode", opusDecode, METH_VARARGS, nullptr},
    {nullptr, nullptr, 0, nullptr},
};

PyModuleDef module = {PyModuleDef_HEAD_INIT, "_dsp", nullptr, -1, methods};

}  //namespace

PyMODINIT_FUNC PyInit__dsp() {
    return PyModule_Create(&module);
}

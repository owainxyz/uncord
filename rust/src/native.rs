use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyList, PyString};
use std::fmt::Write;

const DIACRITICS: [u32; 297] = [
    0x0305, 0x030d, 0x030e, 0x0310, 0x0312, 0x033d, 0x033e, 0x033f, 0x0346, 0x034a, 0x034b, 0x034c, 0x0350, 0x0351,
    0x0352, 0x0357, 0x035b, 0x0363, 0x0364, 0x0365, 0x0366, 0x0367, 0x0368, 0x0369, 0x036a, 0x036b, 0x036c, 0x036d,
    0x036e, 0x036f, 0x0483, 0x0484, 0x0485, 0x0486, 0x0487, 0x0592, 0x0593, 0x0594, 0x0595, 0x0597, 0x0598, 0x0599,
    0x059c, 0x059d, 0x059e, 0x059f, 0x05a0, 0x05a1, 0x05a8, 0x05a9, 0x05ab, 0x05ac, 0x05af, 0x05c4, 0x0610, 0x0611,
    0x0612, 0x0613, 0x0614, 0x0615, 0x0616, 0x0617, 0x0657, 0x0658, 0x0659, 0x065a, 0x065b, 0x065d, 0x065e, 0x06d6,
    0x06d7, 0x06d8, 0x06d9, 0x06da, 0x06db, 0x06dc, 0x06df, 0x06e0, 0x06e1, 0x06e2, 0x06e4, 0x06e7, 0x06e8, 0x06eb,
    0x06ec, 0x0730, 0x0732, 0x0733, 0x0735, 0x0736, 0x073a, 0x073d, 0x073f, 0x0740, 0x0741, 0x0743, 0x0745, 0x0747,
    0x0749, 0x074a, 0x07eb, 0x07ec, 0x07ed, 0x07ee, 0x07ef, 0x07f0, 0x07f1, 0x07f3, 0x0816, 0x0817, 0x0818, 0x0819,
    0x081b, 0x081c, 0x081d, 0x081e, 0x081f, 0x0820, 0x0821, 0x0822, 0x0823, 0x0825, 0x0826, 0x0827, 0x0829, 0x082a,
    0x082b, 0x082c, 0x082d, 0x0951, 0x0953, 0x0954, 0x0f82, 0x0f83, 0x0f86, 0x0f87, 0x135d, 0x135e, 0x135f, 0x17dd,
    0x193a, 0x1a17, 0x1a75, 0x1a76, 0x1a77, 0x1a78, 0x1a79, 0x1a7a, 0x1a7b, 0x1a7c, 0x1b6b, 0x1b6d, 0x1b6e, 0x1b6f,
    0x1b70, 0x1b71, 0x1b72, 0x1b73, 0x1cd0, 0x1cd1, 0x1cd2, 0x1cda, 0x1cdb, 0x1ce0, 0x1dc0, 0x1dc1, 0x1dc3, 0x1dc4,
    0x1dc5, 0x1dc6, 0x1dc7, 0x1dc8, 0x1dc9, 0x1dcb, 0x1dcc, 0x1dd1, 0x1dd2, 0x1dd3, 0x1dd4, 0x1dd5, 0x1dd6, 0x1dd7,
    0x1dd8, 0x1dd9, 0x1dda, 0x1ddb, 0x1ddc, 0x1ddd, 0x1dde, 0x1ddf, 0x1de0, 0x1de1, 0x1de2, 0x1de3, 0x1de4, 0x1de5,
    0x1de6, 0x1dfe, 0x20d0, 0x20d1, 0x20d4, 0x20d5, 0x20d6, 0x20d7, 0x20db, 0x20dc, 0x20e1, 0x20e7, 0x20e9, 0x20f0,
    0x2cef, 0x2cf0, 0x2cf1, 0x2de0, 0x2de1, 0x2de2, 0x2de3, 0x2de4, 0x2de5, 0x2de6, 0x2de7, 0x2de8, 0x2de9, 0x2dea,
    0x2deb, 0x2dec, 0x2ded, 0x2dee, 0x2def, 0x2df0, 0x2df1, 0x2df2, 0x2df3, 0x2df4, 0x2df5, 0x2df6, 0x2df7, 0x2df8,
    0x2df9, 0x2dfa, 0x2dfb, 0x2dfc, 0x2dfd, 0x2dfe, 0x2dff, 0xa66f, 0xa67c, 0xa67d, 0xa6f0, 0xa6f1, 0xa8e0, 0xa8e1,
    0xa8e2, 0xa8e3, 0xa8e4, 0xa8e5, 0xa8e6, 0xa8e7, 0xa8e8, 0xa8e9, 0xa8ea, 0xa8eb, 0xa8ec, 0xa8ed, 0xa8ee, 0xa8ef,
    0xa8f0, 0xa8f1, 0xaab0, 0xaab2, 0xaab3, 0xaab7, 0xaab8, 0xaabe, 0xaabf, 0xaac1, 0xfe20, 0xfe21, 0xfe22, 0xfe23,
    0xfe24, 0xfe25, 0xfe26, 0x10a0f, 0x10a38, 0x1d185, 0x1d186, 0x1d187, 0x1d188, 0x1d189, 0x1d1aa, 0x1d1ab, 0x1d1ac,
    0x1d1ad, 0x1d242, 0x1d243, 0x1d244,
];
const PLACEHOLDER: char = '\u{10EEEE}';
pub const MAX_CELLS: usize = DIACRITICS.len();

fn bytesOf<'py>(obj: &Bound<'py, PyAny>) -> PyResult<Bound<'py, PyBytes>> {
    if let Ok(b) = obj.cast::<PyBytes>() {
        return Ok(b.clone());
    }
    Ok(obj.py().get_type::<PyBytes>().call1((obj,))?.cast_into::<PyBytes>()?)
}

#[pyfunction]
#[pyo3(name = "hasPixels")]
pub fn hasPixels(arg: &Bound<'_, PyAny>) -> PyResult<bool> {
    let owned;
    let s: &[u8] = if let Ok(st) = arg.cast::<PyString>() {
        owned = st.to_str()?.as_bytes().to_vec();
        &owned
    } else if let Ok(b) = arg.cast::<PyBytes>() {
        b.as_bytes()
    } else {
        return Err(PyTypeError::new_err("expected str or bytes"));
    };
    let Some(q) = memchr::memchr(b'q', s) else { return Ok(false) };
    let mut p = q + 1;
    while p < s.len() {
        let c = s[p];
        if c == 0x1b {
            break;
        }
        if c == b'#' || c == b'"' {
            p += 1;
            while p < s.len() && (s[p].is_ascii_digit() || s[p] == b';') {
                p += 1;
            }
            continue;
        }
        if (b'@'..=b'~').contains(&c) {
            return Ok(true);
        }
        p += 1;
    }
    Ok(false)
}

#[pyfunction]
#[pyo3(name = "placeholderRow")]
pub fn placeholderRow(row: isize, x0: isize, width: isize) -> PyResult<String> {
    let n = MAX_CELLS as isize;
    if row < 0 || x0 < 0 || width < 0 || row >= n || x0 + width > n {
        return Err(PyValueError::new_err("row or column out of range"));
    }
    let r = char::from_u32(DIACRITICS[row as usize]).unwrap();
    let mut out = String::with_capacity(width as usize * 8);
    for i in 0..width as usize {
        out.push(PLACEHOLDER);
        out.push(r);
        out.push(char::from_u32(DIACRITICS[x0 as usize + i]).unwrap());
    }
    Ok(out)
}

fn findStart(s: &[u8], from: usize) -> Option<usize> {
    let mut i = from;
    while i + 2 < s.len() {
        let z = i + memchr::memchr(0, &s[i..s.len() - 2])?;
        if s[z + 1] == 0 && s[z + 2] == 1 {
            return Some(z);
        }
        i = z + 1;
    }
    None
}

#[pyfunction]
#[pyo3(name = "splitAnnexb")]
pub fn splitAnnexb<'py>(py: Python<'py>, arg: &Bound<'py, PyAny>) -> PyResult<Bound<'py, PyList>> {
    let held = bytesOf(arg)?;
    let s = held.as_bytes();
    let out = PyList::empty(py);
    let mut start = findStart(s, 0);
    while let Some(st) = start {
        let begin = st + 3;
        let next = findStart(s, begin);
        let mut end = next.unwrap_or(s.len());
        if next.is_some() && end > begin && s[end - 1] == 0 {
            end -= 1;
        }
        if end > begin {
            out.append(PyBytes::new(py, &s[begin..end]))?;
        }
        start = next;
    }
    Ok(out)
}

#[pyfunction]
#[pyo3(name = "fuaPayloads")]
pub fn fuaPayloads<'py>(py: Python<'py>, seq: &Bound<'py, PyAny>, mtu: isize) -> PyResult<Bound<'py, PyList>> {
    if mtu < 3 {
        return Err(PyValueError::new_err("mtu too small"));
    }
    let mtu = mtu as usize;
    let out = PyList::empty(py);
    for item in seq.try_iter().map_err(|_| PyTypeError::new_err("expected a list of nal units"))? {
        let item = item?;
        let Ok(b) = item.cast::<PyBytes>() else {
            return Err(PyTypeError::new_err("nal units must be bytes"));
        };
        let nal = b.as_bytes();
        if nal.is_empty() {
            continue;
        }
        if nal.len() <= mtu {
            out.append(&item)?;
            continue;
        }
        let ind = (nal[0] & 0xE0) | 28;
        let typ = nal[0] & 0x1F;
        let body = &nal[1..];
        let mut off = 0;
        while off < body.len() {
            let chunk = (body.len() - off).min(mtu);
            let mut pkt = Vec::with_capacity(chunk + 2);
            pkt.push(ind);
            pkt.push((if off == 0 { 0x80 } else { 0 }) | (if off + mtu >= body.len() { 0x40 } else { 0 }) | typ);
            pkt.extend_from_slice(&body[off..off + chunk]);
            out.append(PyBytes::new(py, &pkt))?;
            off += mtu;
        }
    }
    Ok(out)
}

#[pyfunction]
#[pyo3(name = "rtpHeader")]
pub fn rtpHeader(arg: &Bound<'_, PyAny>) -> PyResult<Option<(usize, u8, bool, u16, u32, u32)>> {
    let held = bytesOf(arg)?;
    let d = held.as_bytes();
    if d.len() < 16 || (d[0] >> 6) != 2 {
        return Ok(None);
    }
    let hlen = 12 + 4 * (d[0] & 0x0F) as usize + if d[0] & 0x10 != 0 { 4 } else { 0 };
    if hlen > d.len() {
        return Ok(None);
    }
    let word = |i: usize| u32::from_be_bytes([d[i], d[i + 1], d[i + 2], d[i + 3]]);
    Ok(Some((hlen, d[1] & 0x7F, d[1] & 0x80 != 0, u16::from_be_bytes([d[2], d[3]]), word(4), word(8))))
}

fn sixelRun(o: &mut String, count: usize, c: char) {
    if count >= 4 {
        let _ = write!(o, "!{count}{c}");
    } else {
        for _ in 0..count {
            o.push(c);
        }
    }
}

const HASH_SIZE: usize = 1024;

#[pyfunction]
#[pyo3(signature = (pixels, w, h, palette=None))]
pub fn sixel(pixels: &Bound<'_, PyAny>, w: isize, h: isize, palette: Option<&Bound<'_, PyAny>>) -> PyResult<Option<String>> {
    let heldPx = bytesOf(pixels)?;
    let px = heldPx.as_bytes();
    let usePal = palette.is_some_and(|p| !p.is_none());
    let per = if usePal { 1 } else { 3 };
    if w <= 0 || h <= 0 || (px.len() as isize) < w * h * per {
        return Err(PyValueError::new_err("pixels don't match the size"));
    }
    let (w, h) = (w as usize, h as usize);
    let mut idx = vec![0u8; w * h];
    let mut pal = [0u8; 768];
    let mut ncolours = 0usize;
    if usePal {
        let heldPal = bytesOf(palette.unwrap())?;
        let p = heldPal.as_bytes();
        ncolours = (p.len() / 3).min(256);
        pal[..ncolours * 3].copy_from_slice(&p[..ncolours * 3]);
        for i in 0..w * h {
            if px[i] as usize >= ncolours {
                return Err(PyValueError::new_err("palette index out of range"));
            }
            idx[i] = px[i];
        }
    } else {
        let mut keys = [0u32; HASH_SIZE];
        let mut vals = [-1i16; HASH_SIZE];
        for i in 0..w * h {
            let rgb = (px[i * 3] as u32) << 16 | (px[i * 3 + 1] as u32) << 8 | px[i * 3 + 2] as u32;
            let mut slot = (rgb.wrapping_mul(2654435761) >> 22) as usize;
            let c = loop {
                if vals[slot] < 0 {
                    if ncolours >= 256 {
                        return Ok(None);
                    }
                    keys[slot] = rgb;
                    vals[slot] = ncolours as i16;
                    pal[ncolours * 3] = (rgb >> 16) as u8;
                    pal[ncolours * 3 + 1] = (rgb >> 8) as u8;
                    pal[ncolours * 3 + 2] = rgb as u8;
                    ncolours += 1;
                    break ncolours - 1;
                }
                if keys[slot] == rgb {
                    break vals[slot] as usize;
                }
                slot = (slot + 1) & (HASH_SIZE - 1);
            };
            idx[i] = c as u8;
        }
    }
    let mut o = String::with_capacity(w * h / 2 + 64);
    let _ = write!(o, "\x1bP0;0;0q\"1;1;{w};{h}");
    for c in 0..ncolours {
        let pct = |v: u8| (v as u32 * 100 + 127) / 255;
        let _ = write!(o, "#{c};2;{};{};{}", pct(pal[c * 3]), pct(pal[c * 3 + 1]), pct(pal[c * 3 + 2]));
    }
    let mut masks = vec![0u8; 256 * w];
    let mut first = [0usize; 256];
    let mut last = [0usize; 256];
    let mut inBand = [false; 256];
    let mut used: Vec<u8> = Vec::with_capacity(256);
    let mut y0 = 0;
    while y0 < h {
        used.clear();
        let bandH = (h - y0).min(6);
        for r in 0..bandH {
            let row = &idx[(y0 + r) * w..(y0 + r + 1) * w];
            for (x, &c) in row.iter().enumerate() {
                let ci = c as usize;
                if !inBand[ci] {
                    inBand[ci] = true;
                    used.push(c);
                    first[ci] = x;
                    last[ci] = x;
                }
                masks[ci * w + x] |= 1 << r;
                first[ci] = first[ci].min(x);
                last[ci] = last[ci].max(x);
            }
        }
        for (k, &c) in used.iter().enumerate() {
            let ci = c as usize;
            let m = &mut masks[ci * w..(ci + 1) * w];
            if k > 0 {
                o.push('$');
            }
            let _ = write!(o, "#{ci}");
            sixelRun(&mut o, first[ci], '?');
            let mut x = first[ci];
            while x <= last[ci] {
                let mut run = 1;
                while x + run <= last[ci] && m[x + run] == m[x] {
                    run += 1;
                }
                sixelRun(&mut o, run, (63 + m[x]) as char);
                x += run;
            }
            m[first[ci]..=last[ci]].fill(0);
            inBand[ci] = false;
        }
        o.push('-');
        y0 += 6;
    }
    o.push_str("\x1b\\");
    Ok(Some(o))
}

const B64: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

fn base64Into(src: &[u8], out: &mut [u8]) {
    let whole = src.len() / 3;
    for (c, o) in src.chunks_exact(3).zip(out.chunks_exact_mut(4)) {
        let v = (c[0] as u32) << 16 | (c[1] as u32) << 8 | c[2] as u32;
        o[0] = B64[(v >> 18) as usize & 63];
        o[1] = B64[(v >> 12) as usize & 63];
        o[2] = B64[(v >> 6) as usize & 63];
        o[3] = B64[v as usize & 63];
    }
    let rest = &src[whole * 3..];
    if !rest.is_empty() {
        let o = &mut out[whole * 4..whole * 4 + 4];
        let v = (rest[0] as u32) << 16 | (*rest.get(1).unwrap_or(&0) as u32) << 8;
        o[0] = B64[(v >> 18) as usize & 63];
        o[1] = B64[(v >> 12) as usize & 63];
        o[2] = if rest.len() > 1 { B64[(v >> 6) as usize & 63] } else { b'=' };
        o[3] = b'=';
    }
}

#[pyfunction]
#[pyo3(name = "kittyChunks")]
pub fn kittyChunks(data: &Bound<'_, PyAny>, firstKeys: &str, restKeys: &str) -> PyResult<String> {
    let held = bytesOf(data)?;
    let d = held.as_bytes();
    let encLen = d.len().div_ceil(3) * 4;
    let chunks = encLen.div_ceil(4096);
    let head = |k: usize| {
        let keys = if k == 0 { firstKeys } else { restKeys };
        3 + keys.len() + usize::from(!keys.is_empty()) + 4
    };
    let total = encLen + (0..chunks).map(|k| head(k) + 2).sum::<usize>();
    let mut o = vec![0u8; total];
    let mut at = 0;
    for k in 0..chunks {
        let off = k * 4096;
        let chunk = (encLen - off).min(4096);
        let keys = if k == 0 { firstKeys } else { restKeys };
        let mut put = |b: &[u8]| {
            o[at..at + b.len()].copy_from_slice(b);
            at += b.len();
        };
        put(b"\x1b_G");
        put(keys.as_bytes());
        if !keys.is_empty() {
            put(b",");
        }
        put(if off + chunk < encLen { b"m=1;" } else { b"m=0;" });
        let src = &d[off / 4 * 3..((off + chunk) / 4 * 3).min(d.len())];
        base64Into(src, &mut o[at..at + chunk]);
        at += chunk;
        o[at..at + 2].copy_from_slice(b"\x1b\\");
        at += 2;
    }
    Ok(String::from_utf8(o).expect("ascii"))
}

fn isSpace(c: u8) -> bool {
    matches!(c, b' ' | b'\t' | b'\n' | b'\r' | 0x0b | 0x0c)
}

#[pyfunction]
#[pyo3(name = "ppmFrames")]
pub fn ppmFrames(arg: &Bound<'_, PyAny>) -> PyResult<Vec<(usize, usize, usize)>> {
    let held = bytesOf(arg)?;
    let d = held.as_bytes();
    let n = d.len();
    let mut pos = 0;
    let mut out = Vec::new();
    while pos < n {
        let mut p = pos;
        let mut tok = [(0usize, 0usize); 4];
        for t in tok.iter_mut() {
            while p < n && isSpace(d[p]) {
                p += 1;
            }
            let mut q = p;
            while q < n && !isSpace(d[q]) {
                q += 1;
            }
            *t = (p, q);
            p = q;
        }
        p += 1;
        if tok[0].1 - tok[0].0 != 2 || d[tok[0].0] != b'P' || d[tok[0].0 + 1] != b'6' {
            break;
        }
        let mut dims = [0usize; 2];
        let mut ok = true;
        for k in 0..2 {
            let (a, b) = tok[k + 1];
            if a == b || b - a > 6 {
                ok = false;
            }
            let mut v = 0usize;
            for &c in &d[a..b] {
                if !ok {
                    break;
                }
                if !c.is_ascii_digit() {
                    ok = false;
                }
                v = v.wrapping_mul(10).wrapping_add((c as usize).wrapping_sub(b'0' as usize));
            }
            dims[k] = v;
        }
        if !ok {
            break;
        }
        let size = dims[0].saturating_mul(dims[1]).saturating_mul(3);
        if p > n || size > n - p {
            break;
        }
        out.push((dims[0], dims[1], p));
        pos = p + size;
    }
    Ok(out)
}

#![allow(non_snake_case)]
mod md;
mod native;

use pyo3::prelude::*;

struct Entry {
    text: String,
    chars: usize,
}

#[allow(non_snake_case)]
fn charIndex(hay: &str, byte: usize) -> usize {
    hay[..byte].chars().count()
}

#[allow(non_snake_case)]
fn isSubsequence(hay: &str, needle: &[char]) -> bool {
    let mut it = hay.chars();
    needle.iter().all(|c| it.any(|h| h == *c))
}

#[allow(non_snake_case)]
fn score(entry: &Entry, words: &[&str], squashed: &[char]) -> Option<usize> {
    let hay = entry.text.as_str();
    if words.iter().all(|w| hay.contains(w)) {
        let first = words[0];
        let at = hay.find(first).map(|b| charIndex(hay, b)).unwrap_or(0);
        return Some(at + if hay.starts_with(first) { 0 } else { 50 });
    }
    if isSubsequence(hay, squashed) {
        return Some(1000 + entry.chars);
    }
    None
}

#[pyclass]
struct Matcher {
    entries: Vec<Entry>,
}

#[pymethods]
impl Matcher {
    #[new]
    fn new(haystacks: Vec<String>) -> Self {
        let entries = haystacks
            .into_iter()
            .map(|text| {
                let chars = text.chars().count();
                Entry { text, chars }
            })
            .collect();
        Matcher { entries }
    }

    fn __len__(&self) -> usize {
        self.entries.len()
    }

    #[pyo3(signature = (query, limit=250))]
    fn search(&self, py: Python<'_>, query: &str, limit: usize) -> Vec<usize> {
        let words: Vec<&str> = query.split_whitespace().collect();
        if words.is_empty() {
            return (0..self.entries.len().min(limit)).collect();
        }
        let squashed: Vec<char> = query.chars().filter(|c| *c != ' ').collect();
        py.detach(|| {
            let mut scored: Vec<(usize, usize)> = self
                .entries
                .iter()
                .enumerate()
                .filter_map(|(i, e)| score(e, &words, &squashed).map(|s| (s, i)))
                .collect();
            if scored.len() > limit {
                scored.select_nth_unstable(limit);
                scored.truncate(limit);
            }
            scored.sort_unstable();
            scored.into_iter().map(|(_s, i)| i).collect()
        })
    }
}

#[pymodule]
fn _fast(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Matcher>()?;
    m.add_function(wrap_pyfunction!(md::mdLines, m)?)?;
    m.add_function(wrap_pyfunction!(md::mdInline, m)?)?;
    m.add_function(wrap_pyfunction!(md::shortUrlPy, m)?)?;
    m.add_function(wrap_pyfunction!(native::hasPixels, m)?)?;
    m.add_function(wrap_pyfunction!(native::placeholderRow, m)?)?;
    m.add_function(wrap_pyfunction!(native::splitAnnexb, m)?)?;
    m.add_function(wrap_pyfunction!(native::fuaPayloads, m)?)?;
    m.add_function(wrap_pyfunction!(native::rtpHeader, m)?)?;
    m.add_function(wrap_pyfunction!(native::sixel, m)?)?;
    m.add_function(wrap_pyfunction!(native::kittyChunks, m)?)?;
    m.add_function(wrap_pyfunction!(native::ppmFrames, m)?)?;
    m.add("maxCells", native::MAX_CELLS)?;
    Ok(())
}

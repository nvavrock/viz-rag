# Build JSONL chunk files for embedding / RAG retrieval.
# Usage: source("ingest/build_corpus.R"); build_corpus()

library(jsonlite)

split_sections <- function(text) {
  parts <- strsplit(text, "\n(?=## )", perl = TRUE)[[1]]
  if (length(parts) == 1L) {
    return(list(list(heading = "", body = text)))
  }
  lapply(parts, function(part) {
    lines <- strsplit(part, "\n", fixed = TRUE)[[1]]
    heading <- if (grepl("^## ", lines[1])) sub("^## ", "", lines[1]) else ""
    body <- paste(if (heading == "") lines else lines[-1], collapse = "\n")
    list(heading = heading, body = trimws(body))
  })
}

write_chunk <- function(chunks, con, source, path, section, text, meta = list()) {
  if (!nzchar(trimws(text))) {
    return(invisible(NULL))
  }
  row <- c(
    list(
      id = paste0(length(chunks) + 1L),
      source = source,
      path = path,
      section = section,
      text = text
    ),
    meta
  )
  cat(toJSON(row, auto_unbox = TRUE), "\n", file = con, append = TRUE)
  invisible(length(chunks) + 1L)
}

ingest_rmd <- function(path, source, meta, con, chunks_len) {
  text <- paste(readLines(path, warn = FALSE), collapse = "\n")
  yaml_end <- regexpr("\n---\n", text, fixed = TRUE)[1]
  if (yaml_end > 0) {
    text <- substr(text, yaml_end + 5, nchar(text))
  }
  sections <- split_sections(text)
  rel <- path
  for (sec in sections) {
    label <- if (nzchar(sec$heading)) sec$heading else basename(path)
    write_chunk(
      list(), con, source, rel, label, sec$body, meta
    )
  }
}

ingest_markdown <- function(path, source, meta, con) {
  text <- paste(readLines(path, warn = FALSE), collapse = "\n")
  sections <- split_sections(text)
  rel <- path
  for (sec in sections) {
    label <- if (nzchar(sec$heading)) sec$heading else basename(path)
    write_chunk(list(), con, source, rel, label, sec$body, meta)
  }
}

strip_html <- function(html) {
  html <- gsub("<script[^>]*>[\\s\\S]*?</script>", " ", html, perl = TRUE, ignore.case = TRUE)
  html <- gsub("<style[^>]*>[\\s\\S]*?</style>", " ", html, perl = TRUE, ignore.case = TRUE)
  html <- gsub("<[^>]+>", " ", html)
  html <- gsub("&nbsp;", " ", html, fixed = TRUE)
  html <- gsub("&amp;", "&", html, fixed = TRUE)
  html <- gsub("\\s+", " ", html)
  trimws(html)
}

ingest_html_caveat <- function(path, source, meta, con) {
  html <- paste(readLines(path, warn = FALSE), collapse = "\n")
  title <- sub(".*<title>([^<]+)</title>.*", "\\1", html)
  if (identical(title, html)) title <- basename(path)
  body <- strip_html(html)
  write_chunk(list(), con, source, path, title, body, meta)
}

ingest_r_file <- function(path, source, meta, con) {
  text <- paste(readLines(path, warn = FALSE), collapse = "\n")
  rel <- tryCatch(
    sub(paste0("^", normalizePath(project_root, winslash = "/"), "/?"), "", normalizePath(path, winslash = "/")),
    error = function(e) path
  )
  write_chunk(list(), con, source, rel, basename(path), text, meta)
}

build_corpus <- function(project_root = ".") {
  project_root <- normalizePath(project_root, winslash = "/", mustWork = FALSE)
  sources <- file.path(project_root, "sources")
  out_dir <- file.path(project_root, "chunks")
  dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
  out_file <- file.path(out_dir, "corpus.jsonl")
  if (file.exists(out_file)) file.remove(out_file)
  file.create(out_file)

  # data_to_viz stories
  dtv <- file.path(sources, "data_to_viz")
  if (dir.exists(dtv)) {
    rmds <- list.files(file.path(dtv, "story"), pattern = "\\.Rmd$", full.names = TRUE)
    for (f in rmds) {
      ingest_rmd(
        f, "data_to_viz",
        list(language = "r", role = "chart_selection", package = "ggplot2"),
        out_file, 0
      )
    }
    readme <- file.path(dtv, "Example_dataset", "Readme.md")
    if (file.exists(readme)) {
      ingest_markdown(
        readme, "data_to_viz",
        list(language = "r", role = "data_shape", package = "ggplot2"),
        out_file
      )
    }
    caveat_dir <- file.path(dtv, "caveat")
    if (dir.exists(caveat_dir)) {
      htmls <- list.files(caveat_dir, pattern = "\\.html$", full.names = TRUE)
      for (f in htmls) {
        ingest_html_caveat(
          f, "data_to_viz",
          list(language = "en", role = "caveat"),
          out_file
        )
      }
    }
  } else {
    message("Missing sources/data_to_viz — run scripts/fetch_sources.sh first")
  }

  # ggplot2 vignettes
  ggp <- file.path(sources, "ggplot2", "vignettes")
  if (dir.exists(ggp)) {
  vignettes <- list.files(ggp, pattern = "\\.(qmd|Rmd)$", full.names = TRUE)
    for (f in vignettes) {
      ingest_rmd(
        f, "ggplot2",
        list(language = "r", role = "implementation", package = "ggplot2"),
        out_file, 0
      )
    }
  } else {
    message("Missing sources/ggplot2 — run scripts/fetch_sources.sh first")
  }

  # Local curated markdown
  for (subdir in c("corpus/style", "corpus/notes")) {
    dir_path <- file.path(project_root, subdir)
    if (!dir.exists(dir_path)) next
    mds <- list.files(dir_path, pattern = "\\.md$", full.names = TRUE)
    for (f in mds) {
      role <- if (grepl("style", subdir)) "style" else "theory"
      ingest_markdown(
        f, "local",
        list(language = "en", role = role, package = "ggplot2"),
        out_file
      )
    }
  }

  # Optional: personal R recipes from tidytuesday
  tt_r <- normalizePath(file.path(project_root, "../tidytuesday/2026_06_16_uk_baby_names/R"), winslash = "/", mustWork = FALSE)
  if (dir.exists(tt_r)) {
    r_files <- list.files(tt_r, pattern = "\\.R$", full.names = TRUE)
    r_files <- r_files[!grepl("paths\\.R$", r_files)]
    for (f in r_files) {
      ingest_r_file(
        f, "tidytuesday",
        list(language = "r", role = "recipe", package = "ggplot2"),
        out_file
      )
    }
  }

  n <- length(readLines(out_file))
  message("Wrote ", n, " chunks to ", out_file)
  invisible(out_file)
}

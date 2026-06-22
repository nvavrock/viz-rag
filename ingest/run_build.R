# Runner for command-line: Rscript ingest/run_build.R
root <- normalizePath(file.path(dirname(sys.frame(1)$ofile %||% "."), ".."), winslash = "/", mustWork = FALSE)
if (!dir.exists(root)) {
  root <- normalizePath("..", winslash = "/", mustWork = FALSE)
}
source(file.path(root, "ingest/build_corpus.R"))
build_corpus(root)

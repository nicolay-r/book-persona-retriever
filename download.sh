# pg-19
gsutil -m cp -r \
  "gs://deepmind-gutenberg/LICENSE" \
  "gs://deepmind-gutenberg/README.md" \
  "gs://deepmind-gutenberg/metadata.csv" \
  "gs://deepmind-gutenberg/test" \
  "gs://deepmind-gutenberg/test_$folder$" \
  "gs://deepmind-gutenberg/train" \
  "gs://deepmind-gutenberg/train_$folder$" \
  "gs://deepmind-gutenberg/validation" \
  "gs://deepmind-gutenberg/validation_$folder$" \
  ./data/pg19

# wikiplots
https://www.dropbox.com/s/24pa44w7u7wvtma/plots.zip?dl=1

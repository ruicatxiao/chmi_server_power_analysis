# Makefile for CHMI Server Power Analysis
# Regenerate all artifacts from the raw data.

.PHONY: all data figures interactive animations stats clean serve

all: data figures interactive animations stats

data:
	python src/pipeline.py

figures:
	python src/make_figures.py

interactive:
	python src/make_interactive.py

animations:
	python src/make_animations.py

stats:
	python src/compute_stats.py

serve:
	python -m http.server 8000

clean:
	rm -rf figures/*.png interactive/*.html animations/*.mp4

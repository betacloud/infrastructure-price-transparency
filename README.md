# Infrastructure price transparency

The visualization is based on https://github.com/catalyst-cloud/catalystcloud-price-comparison.
Consult the documentation there for explanations of the visualization.

```
$ docker build -t price-comparison .
$ docker run -v $(pwd):/home -it price-comparison
# python src/analyse.py
Downloaded Betacloud prices, with 8 items.
[...]
Saving resulting datasets.
# python src/visualise.py
```

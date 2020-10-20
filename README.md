# Infrastructure price transparency

This tool demonstrates how complex a price comparison of simple infrastructure
resources from different CSPs is at present.

As an example, only individual small and large CSPs are evaluated. The goal
of the tool is not to realize a general price transparency between CSPs.
This would be too imprecise and inefficient with this approach.

## Usage

```
$ docker build -t price-comparison .
$ docker run -v $(pwd):/home -it price-comparison
# python src/analyse.py
Downloaded Betacloud prices, with 8 items.
[...]
Saving resulting datasets.
# python src/visualise.py
```

## References

The visualization is based on https://github.com/catalyst-cloud/catalystcloud-price-comparison.
Consult the documentation there for explanations of the visualization.

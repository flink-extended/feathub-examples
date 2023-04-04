# FeatHub Examples

This project provides example programs for key
[FeatHub](https://github.com/alibaba/feathub) APIs and functionalities.

## Table of Contents

- [Flink - DerivedFeatureView](flink-derived-feature-view)
- [Flink - SlidingFeatureView](flink-sliding-feature-view)
- [Flink - Read and Write HDFS](flink-read-write-hdfs)
- [Flink - Read and Write Redis](flink-read-write-redis)
- [Flink - Read and Write MySQL](flink-read-write-mysql)
- [Spark - DerivedFeatureView](spark-derived-feature-view)


## Code Formatting Guide

This project uses [Black](https://black.readthedocs.io/en/stable/index.html) to
format Python code, [flake8](https://flake8.pycqa.org/en/latest/) to check
Python code style, and [mypy](https://mypy.readthedocs.io/en/stable/) to check
type annotation.

Run the following command to format codes, check code style, and check type annotation 
before uploading PRs for review.

```bash
# Format python code
$ python -m black .

# Check python code style
$ python -m flake8 --config=setup.cfg .

# Check python type annotation
$ python -m mypy --config-file setup.cfg .
```

## Contact Us

Chinese-speaking users are recommended to join the following DingTalk group for
FeatHub-related questions and discussion.

<img src="figures/dingtalk.png" width="20%" height="auto">

English-speaking users can use this [invitation
link](https://join.slack.com/t/feathubworkspace/shared_invite/zt-1ik9wk0xe-MoMEotpCEYvRRc3ulpvg2Q)
to join our [Slack channel](https://feathub.slack.com/) for questions and
discussion.

We are actively looking for user feedback and contributors from the community.
Please feel free to create pull requests and open Github issues for feedback and
feature requests.

Come join us!


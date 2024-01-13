#!/usr/bin/env bash
set -euo pipefail

D=20240106_compare_classifiers

ap_plot_metrics $D/cnn $D/resnet_alpha $D/densenet -o cnn_resnet_densenet.svg

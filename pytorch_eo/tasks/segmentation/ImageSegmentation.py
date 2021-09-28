import torch
import torch.nn.functional as F
from einops import rearrange

from pytorch_eo.metrics.segmentation import iou
from ..BaseTask import BaseTask


class ImageSegmentation(BaseTask):

    def __init__(self, model, hparams=None, inputs=['image'], outputs=['mask'], loss_fn=None, metrics=None):

        # defaults
        loss_fn = torch.nn.BCEWithLogitsLoss() if loss_fn is None else loss_fn
        hparams = {'optimizer': 'Adam'} if hparams is None else hparams
        metrics = {'iou': iou} if metrics is None else metrics

        super().__init__(model, hparams, inputs, outputs, loss_fn, metrics)

    def compute_loss(self, y_hat, y):
        return self.loss_fn(y_hat, y['mask'])

    def compute_metrics(self, y_hat, y):
        return {metric_name: metric(y_hat, y['mask']) for metric_name, metric in self.metrics.items()}

    def predict(self, batch):
        self.eval()
        with torch.no_grad():
            x = {k: v.to(self.device) for k, v in batch.items() if k in self.inputs}
            y_hat = self(x)
            return torch.sigmoid(y_hat)
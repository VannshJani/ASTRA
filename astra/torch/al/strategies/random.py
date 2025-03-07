import numpy as np
import torch
import torch.nn as nn
from astra.torch.al.strategies.base import Strategy
from astra.torch.al.acquisitions.base import RandomAcquisition
from astra.torch.al.errors import AcquisitionMismatchError

from typing import Dict, Sequence, Union


class RandomStrategy(Strategy):
    def __init__(
        self,
        acquisitions: Union[RandomAcquisition, Sequence[RandomAcquisition]],
        inputs: torch.Tensor,
        outputs: torch.Tensor,
    ):
        """Base class for query strategies

        Args:
            acquisitions: A sequence of acquisition functions.
            inputs: A tensor of inputs.
            outputs: A tensor of outputs.
        """
        super().__init__(acquisitions, inputs, outputs)

        for name, acquisition in self.acquisitions.items():
            if not isinstance(acquisition, RandomAcquisition):
                raise AcquisitionMismatchError(RandomAcquisition, acquisition)

    def query(
        self,
        net: nn.Module,
        pool_indices: torch.Tensor,
        context_indices: torch.Tensor = None,
        n_query_samples: int = 1,
        n_mc_samples: int = 10,
        batch_size: int = None,
    ) -> Dict[str, torch.Tensor]:
        """Random query strategy

        Args:
            net: This argument is ignored.
            pool_indices: The indices of the pool set.
            context_indices: This argument is ignored.
            n_query_samples: Number of samples to query.
            n_mc_samples: This argument is used to match the interface of other strategies.
            batch_size: This argument is ignored.

        Returns:
            best_indices: A dictionary of acquisition names and the corresponding best indices.
        """
        assert isinstance(pool_indices, torch.Tensor), f"pool_indices must be a torch.Tensor, got {type(pool_indices)}"

        # logits shape (n_mc_samples, pool_dim, n_classes)
        logits = torch.rand(n_mc_samples, len(pool_indices), self.n_classes)
        best_indices = {}
        for acq_name, acquisition in self.acquisitions.items():
            scores = acquisition.acquire_scores(logits)
            indices = torch.topk(scores, n_query_samples).indices
            selected_indices = pool_indices[indices]
            best_indices[acq_name] = selected_indices

        return best_indices

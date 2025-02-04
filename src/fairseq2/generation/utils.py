# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional, final

from torch import Tensor

from fairseq2.data.text import TextTokenDecoder


@final
class _StdOutPrintHook:
    """Prints characters produced by a sequence generator to stdout."""

    _text_decoder: TextTokenDecoder
    _prev_text_len: int
    _first_print: bool

    def __init__(self, text_decoder: TextTokenDecoder) -> None:
        self._text_decoder = text_decoder
        self._prev_text_len = 0
        self._first_print = True

    def __call__(
        self,
        prompt_indices: Tensor,
        seqs: Tensor,
        step_scores: Optional[Tensor],
        prefill: bool,
    ) -> None:
        if len(prompt_indices) > 1:
            raise RuntimeError(
                "`StdOutPrintHook` can only be used with a single prompt."
            )

        # Do not print anything during prompt prefill.
        if prefill:
            return

        text = self._text_decoder(seqs[0])

        text_len = len(text)

        # If this is our first print, determine the length of the prompt text.
        if self._prev_text_len == 0:
            prev_text = self._text_decoder(seqs[0][:-1])

            prev_text_len = len(prev_text)
        else:
            prev_text_len = self._prev_text_len

        # Cache the length of the text so that we don't have to decode it twice
        # in the next step.
        self._prev_text_len = text_len

        # No need to print if we decoded a control symbol (e.g. EOS).
        if text_len == prev_text_len:
            return

        text = str(text)

        text = text[prev_text_len - text_len :]

        # Some models output several whitespace characters after the prompt.
        if self._first_print:
            text = text.lstrip()
            if not text:
                return

            self._first_print = False

        print(text, end="", flush=True)

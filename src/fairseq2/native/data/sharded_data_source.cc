// Copyright (c) Meta Platforms, Inc. and affiliates.
// All rights reserved.
//
// This source code is licensed under the BSD-style license found in the
// LICENSE file in the root directory of this source tree.

#include "fairseq2/native/data/sharded_data_source.h"

namespace fairseq2::detail {

std::optional<data>
sharded_data_source::next()
{
    for (std::size_t i = 0; i < shard_idx_; i++)
        if (!inner_->next())
            return {};

    std::optional<data> d = inner_->next();
    if (!d)
        return {};

    for (std::size_t i = 0; i < num_shards_ - shard_idx_ - 1; i++)
        if (!inner_->next())
            return {};

    return d;
}

void
sharded_data_source::reset()
{
    inner_->reset();
}

void
sharded_data_source::record_position(tape &t) const
{
    inner_->record_position(t);
}

void
sharded_data_source::reload_position(tape &t)
{
    inner_->reload_position(t);
}

}  // namespace fairseq2::detail

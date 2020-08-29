import staticmaps


def test_sharding() -> None:
    t = staticmaps.TileProvider(name="test", url_pattern="$s/$z/$x/$y", shards=["0", "1", "2"])
    shard_counts = [0, 0, 0]
    for x in range(0, 100):
        for y in range(0, 100):
            u = t.url(0, x, y)
            for s in [0, 1, 2]:
                if u == "{}/0/{}/{}".format(s, x, y):
                    shard_counts[s] += 1
    assert shard_counts[0] + shard_counts[1] + shard_counts[2] == 100 * 100
    third = (100 * 100) // 3
    for s in shard_counts:
        assert (third * 0.9) < s
        assert s < (third * 1.1)

#!/usr/bin/env python
"""py-staticmaps - Example Frankfurt-New York"""

# py-staticmaps
# Copyright (c) 2020 Florian Pigorsch; see /LICENSE for licensing information

import math
import staticmaps

colors = [((0, 0, 0, 0), 0.0),
          ((255, 255, 255, 255), 1.0),
          ((0, 0, 0), 1.0),
          ((255, 255, 255), 1.0),
          ((255, 255, 255, 100), 0.392156627),
          ((255, 255, 255, 200), 0.781250000),
          ]
for rgb, float_alpha in colors:
    color = staticmaps.Color(*rgb)
    print(math.isclose(float_alpha, color.float_a(), rel_tol=0.10))

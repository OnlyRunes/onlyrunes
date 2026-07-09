#!/usr/bin/env python3
# ===========================================================================
#  GENERATED FILE — do not hand-edit.  Edit the fragments in src/ and run
#  `python3 build.py` (build_site.sh does this automatically).  See src/.
# ===========================================================================
"""
OnlyRunes  —  A Text Adventure in Gielinor
==========================================
A terminal text adventure inspired by Old School RuneScape. Explore the cities
of Misthalin, Asgarnia and the Kharidian Desert, train your skills, fight
monsters, bank your loot, trade on the Grand Exchange, unlock members content,
and complete classic quests.

A love letter to Old School RuneScape — not every item, monster or quest, but a
broad, coherent world built to be easy to extend (see the data tables below).

Run with:  python3 adventure.py
"""

import contextlib
import difflib
import io
import json
import math
import os
import random
import sys
import textwrap
import time



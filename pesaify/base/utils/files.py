# -*- coding: utf-8 -*-

import hashlib

from os import path, urandom
from unidecode import unidecode

from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.core.exceptions import ValidationError

from .iterators import split_by_n

from django.utils.deconstruct import deconstructible
from django.template.defaultfilters import filesizeformat

def get_file_path(instance, filename, base_path):
    basename = path.basename(filename).lower()
    base, ext = path.splitext(basename)
    base = slugify(unidecode(base))[0:100]
    basename = "".join([base, ext])

    hash_part = generate_hash_part()

    return path.join(base_path, hash_part, basename)

def generate_hash_part():    
    hs = hashlib.sha256()
    hs.update(force_bytes(timezone.now().isoformat()))
    hs.update(urandom(1024))

    p1, p2, p3, p4, *p5 = split_by_n(hs.hexdigest(), 1)
    hash_part = path.join(p1, p2, p3, p4, "".join(p5))

    return path.join(hash_part)
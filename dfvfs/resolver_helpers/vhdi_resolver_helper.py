# -*- coding: utf-8 -*-
"""The VHD image path specification resolver helper implementation."""

from dfvfs.file_io import vhdi_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper


class VHDIResolverHelper(resolver_helper.ResolverHelper):
  """VHD image resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VHDI

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return vhdi_file_io.VHDIFile(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(VHDIResolverHelper())

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The SleuthKit (TSK) file system implementation."""

import os
import pytsk3

# This is necessary to prevent a circular import.
import pyvfs.vfs.tsk_file_entry

from pyvfs.path import tsk_path_spec
from pyvfs.vfs import file_system


class _TSKFileSystemImage(pytsk3.Img_Info):
  """Class that implements a pytsk3 image object using a file-like object."""

  def __init__(self, file_object):
    """Initializes the image object.

    Args:
      file_object: the file-like object (instance of io.FileIO).

    Raises:
      ValueError: if the file-like object is invalid.
    """
    if not file_object:
      raise ValueError(u'Missing file-like object.')

    self._file_object = file_object
    super(_TSKFileSystemImage, self).__init__()

  # Note: that the following functions do not follow the style guide
  # because they are part of the pytsk3.Img_Info object interface.

  def close(self):
    """Closes the volume IO object."""
    self._file_object = None

  def read(self, offset, size):
    """Reads a byte string from the image object at the specified offset.

    Args:
      offset: offset where to start reading.
      size: number of bytes to read.

    Returns:
      A byte string containing the data read.
    """
    self._file_object.seek(offset, os.SEEK_SET)
    return self._file_object.read(size)

  def get_size(self):
    """Retrieves the size."""
    return self._file_object.get_size()


class TSKFileSystem(file_system.FileSystem):
  """Class that implements a file system object using pytsk3."""

  _LOCATION_ROOT = u'/'

  def __init__(self, file_object, offset=0):
    """Initializes the file system object.

    Args:
      file_object: the file-like object (instance of io.FileIO).
      offset: option offset, in bytes, of the start of the file system,
              the default is 0.
    """
    super(TSKFileSystem, self).__init__()
    self._file_object = file_object

    # We need to keep the pytsk3.Img_Info around due to an issue with
    # reference counting.
    self._tsk_image = _TSKFileSystemImage(file_object)
    self._tsk_file_system = pytsk3.FS_Info(self._tsk_image, offset=offset)

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry).

    Raises:
      ValueError: if the path specification is incorrect.
    """
    # Opening a file by inode number is faster than opening a file by location.
    inode = getattr(path_spec, 'inode', None)
    location = getattr(path_spec, 'location', None)

    if inode is not None:
      tsk_file = self._tsk_file_system.open_meta(inode=inode)
    elif location is not None:
      tsk_file = self._tsk_file_system.open(location)
    else:
      raise ValueError(u'Path specification missing inode and location.')

    return pyvfs.vfs.tsk_file_entry.TSKFileEntry(
        self, path_spec, tsk_file=tsk_file)

  def GetFsInfo(self):
    """Retrieves the file system info object.

    Returns:
      The SleuthKit file system info object (instance of
      pytsk3.FS_Info).
    """
    return self._tsk_file_system

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    tsk_file = self._tsk_file_system.open(self._LOCATION_ROOT)

    path_spec = tsk_path_spec.TSKPathSpec(location=self._LOCATION_ROOT)

    return pyvfs.vfs.tsk_file_entry.TSKFileEntry(
        self, path_spec, tsk_file=tsk_file)
# -*- coding: utf-8 -*-

# This is the Exact Duplicate plugin for MusicBrainz Picard.
# Copyright © 2022 Harrison Boyd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

PLUGIN_NAME = 'Exact Duplicate'
PLUGIN_AUTHOR = 'Harrison Boyd'
PLUGIN_LICENSE = 'GPL-2.0-or-later'
PLUGIN_LICENSE_URL = 'https://www.gnu.org/licenses/gpl-2.0.html'
PLUGIN_DESCRIPTION = '''
Checks to see if any exact duplicate albums exist by taking the album you just added and using your naming script looks to see if any file already exists there.<br />
If the file does exist it brings it into picard and marks the album with an error alerting you that there is a duplicate file'''
PLUGIN_VERSION = "0.5"
PLUGIN_API_VERSIONS = ["2.0"]

from os import path

from picard import log
from picard.album import Album
from picard.file import register_file_post_addition_to_track_processor
from picard.ui.itemviews import BaseAction, register_album_action
from PyQt5 import QtWidgets

duplicates = []
originals = []

class OpenDuplicateFolder(BaseAction):
    NAME = 'Open Duplicate in Explorer'

    def callback(self, objs):
        for album in objs:
            if (isinstance(album, Album)) and ("There is already a copy of this album in your collection" in album.errors):
                self.tagger.remove_album(album)


def findMainWindow():
    # Global function to find the (open) QMainWindow in application
    app = QtWidgets.QApplication.instance()
    for widget in app.topLevelWidgets():
        if isinstance(widget, QtWidgets.QMainWindow):
            return widget
    return None

def file_post_addition_to_track_processor(track, addedFile):
    fullPath = addedFile.make_filename(addedFile.filename, addedFile.metadata)
    if ((not (addedFile.filename == fullPath)) and path.exists(fullPath)):
        try:
            fileAlreadyAdded = False
            for albumTrack in track.album.tracks:
                for trackFile in albumTrack.files:
                    if trackFile.filename == fullPath:
                        fileAlreadyAdded = True
                        break
            if not fileAlreadyAdded:
                findMainWindow().tagger.add_files([fullPath])
                duplicates.append(track)

            for albumTrack in track.album.tracks:
                log.debug("On track" + str(track))
                for trackFile in albumTrack.files:
                    log.debug("On file path " + str(trackFile.filename))
                    if trackFile.filename == fullPath:
                        log.debug(str(trackFile.filename) + " matches " + fullPath)
                        originals.append(albumTrack)

            log.debug("Orgs" + str(originals))
            log.debug("Dups" + str(duplicates))
            if ("There is already a copy of this album in your collection" not in track.album.errors):
                track.album.error_append("There is already a copy of this album in your collection")
                track.album.update(update_tracks=False, update_selection=False)
        except Exception as ex:
            log.debug(ex)
register_album_action(OpenDuplicateFolder())
register_file_post_addition_to_track_processor(file_post_addition_to_track_processor)

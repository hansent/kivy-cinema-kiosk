#This file is part of the Kivy Cinema Kiosk Demo.
#	Copyright (C) 2010 by 
#	Thomas Hansen  <thomas@kivy.org>
#	Mathieu Virbel <mat@kivy.org>
#
#	The Kivy Cinema Kiosk Demo is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	The Kivy Cinema Kiosk Demo is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with The Kivy Cinema Kiosk Demo.  If not, see <http://www.gnu.org/licenses/>.


class Movie(object):
	def __init__(self, movie_data):
		self.title = movie_data["title"];
		self.summary = movie_data["summary"];
		self.rating = movie_data["rating"];
		self.related = movie_data["related"];
		self.show_times = movie_data["show_times"];

	def __repr__(self):
		return "Title:%s | Trailer:%s" % (self.title, self.trailer)

	def set_trailer(self, filepath):
		self.trailer = filepath;
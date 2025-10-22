#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------- #
# Copyright (c) 2021, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2021. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# ----------------------------------------------------------------------- #

import numpy

from orangewidget.widget import Input
from oasys2.canvas.util.canvas_util import add_widget_parameters_to_module

from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D
from wofryimpl.beamline.optical_elements.absorbers.slit import WOSlit
from wofryimpl.beamline.optical_elements.absorbers.beam_stopper import WOBeamStopper
from wofryimpl.beamline.optical_elements.ideal_elements.screen import WOScreen
from wofryimpl.beamline.optical_elements.ideal_elements.ideal_lens import WOIdealLens

from orangecontrib.wofry.util.wofry_objects import WofryData

from syned_gui.beamline_rendering.ow_abstract_beamline_renderer import AbstractBeamlineRenderer, AspectRatioModifier, Orientations, OpticalElementsColors, \
    initialize_arrays, get_height_shift

class BeamlineRenderer2D(AbstractBeamlineRenderer):
    name = "Beamline Renderer 2D"
    description = "Beamline Renderer"
    icon = "icons/renderer.png"
    maintainer = "Luca Rebuffi"
    maintainer_email = "lrebuffi(@at@)anl.gov"
    priority = 1000
    category = "Utility"
    keywords = ["data", "file", "load", "read"]

    class Inputs:
        wofry_data = Input("Wofry Data", WofryData, default=True, auto_summary=False)

    wofry_data = None

    def __init__(self):
        super(BeamlineRenderer2D, self).__init__()

    @Inputs.wofry_data
    def set_input(self, input_data):
        self.setStatusMessage("")

        if not input_data is None:
            self.wofry_data = input_data
            self.perform_rendering(on_receiving_input=True)

    def render_beamline(self):
        if not self.wofry_data is None:
            if not isinstance(self.wofry_data.get_wavefront(), GenericWavefront2D): raise ValueError("The current beamline is not 2D")

            self.figure_canvas.clear_axis()

            beamline = self.wofry_data.get_beamline()

            number_of_elements = beamline.get_beamline_elements_number() + (1 if self.draw_source else 0)

            centers, limits = initialize_arrays(number_of_elements=number_of_elements)

            aspect_ratio_modifier = AspectRatioModifier(element_expansion_factor=[self.element_expansion_factor,
                                                                                  self.element_expansion_factor,
                                                                                  self.element_expansion_factor],
                                                        layout_reduction_factor=[1/self.distance_compression_factor,
                                                                                 1.0,
                                                                                 1,0])
            previous_oe_distance    = 0.0
            previous_image_segment  = 0.0
            previous_image_distance = 0.0
            previous_height = self.initial_height # for better visibility
            previous_shift  = 0.0
            beam_horizontal_inclination = 0.0
            beam_vertical_inclination   = 0.0

            if self.draw_source:
                source             = beamline.get_light_source()
                source_name        = source.get_name()

                self.add_source(centers, limits, length=0.0, height=self.initial_height, aspect_ration_modifier=aspect_ratio_modifier, source_name=source_name)

            oe_index = 0 if self.draw_source else -1

            for beamline_element in beamline.get_beamline_elements():
                oe_index += 1

                coordinates     = beamline_element.get_coordinates()
                optical_element = beamline_element.get_optical_element()

                source_segment = coordinates.p()
                image_segment  = coordinates.q()

                source_distance = source_segment * numpy.cos(beam_vertical_inclination) * numpy.cos(beam_horizontal_inclination)

                segment_to_oe     = previous_image_segment + source_segment
                oe_total_distance = previous_oe_distance   + previous_image_distance + source_distance

                height, shift = get_height_shift(segment_to_oe,
                                                 previous_height,
                                                 previous_shift,
                                                 beam_vertical_inclination,
                                                 beam_horizontal_inclination)

                if isinstance(optical_element, WOScreen):
                    self.add_point(centers, limits, oe_index=oe_index,
                                   distance=oe_total_distance, height=height, shift=shift,
                                   label=None, aspect_ratio_modifier=aspect_ratio_modifier)
                elif isinstance(optical_element, WOIdealLens):
                    self.add_point(centers, limits, oe_index=oe_index,
                                   distance=oe_total_distance, height=height, shift=shift,
                                   label="Ideal Lens", aspect_ratio_modifier=aspect_ratio_modifier)
                elif isinstance(optical_element, WOSlit) or isinstance(optical_element, WOBeamStopper):
                    x_min, x_max, y_min, y_max = optical_element.get_boundary_shape().get_boundaries()
                    aperture = [x_max - x_min, y_max - y_min]

                    if isinstance(optical_element, WOSlit):          label = "Slits"
                    elif isinstance(optical_element, WOBeamStopper): label = "Beam Stopper"

                    self.add_slits_filter(centers, limits, oe_index=oe_index,
                                          distance=oe_total_distance, height=height, shift=shift,
                                          aperture=aperture, label=label, aspect_ratio_modifier=aspect_ratio_modifier)

                image_distance = image_segment * numpy.cos(beam_vertical_inclination) * numpy.cos(beam_horizontal_inclination)  # new direction

                previous_height = height
                previous_shift = shift
                previous_oe_distance = oe_total_distance
                previous_image_segment = image_segment
                previous_image_distance = image_distance

            height, shift = get_height_shift(previous_image_segment,
                                             previous_height,
                                             previous_shift,
                                             beam_vertical_inclination,
                                             beam_horizontal_inclination)

            self.add_point(centers, limits, oe_index=number_of_elements - 1,
                           distance=previous_oe_distance + previous_image_distance,
                           height=height, shift=shift, label="End Point",
                           aspect_ratio_modifier=aspect_ratio_modifier)

            return number_of_elements, centers, limits

add_widget_parameters_to_module(__name__)
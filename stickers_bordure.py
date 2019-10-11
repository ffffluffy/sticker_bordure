#!/usr/bin/env python
import gimpfu
from gimpfu import pdb


def stickerify_bordure(image, current_layer, resize=False, inner_grow=3, outer_grow=12,
                       border_color_fg=(1.0, 1.0, 1.0), border_color_bg=(0.0, 0.0, 0.0),
                       shadow=True, canvas_increase=0):
    def duplicate_layer():
        copy = current_layer.copy()
        image.add_layer(copy)
        # copy is added above so we want to go down a bit
        image.active_layer = current_layer
        return copy

    def fill_bg():
        pdb.gimp_edit_bucket_fill(current_layer, 1, 0, 100, 255, 0, 0, 0)

    def fill_black():
        set_colors(background_color=(0,0,0))
        fill_bg()
        set_colors(foreground_color=border_color_fg, background_color=border_color_bg)

    def fill_fg():
        pdb.gimp_edit_bucket_fill(current_layer, 0, 0, 100, 255, 0, 0, 0)

    def set_colors(foreground_color=(255, 255, 255), background_color=(0, 0, 0)):
        pdb.gimp_context_set_foreground(foreground_color)
        pdb.gimp_context_set_background(background_color)

    pdb.gimp_context_push()
    pdb.gimp_image_undo_group_start(image)

    # clean selection to avoid bugs
    pdb.gimp_selection_none(image)

    # we set the foreground and background color of the border
    set_colors(foreground_color=border_color_fg, background_color=border_color_bg)

    # resize early to avoid compressing the bordure
    if resize:
        width, height = image.width, image.height

        if width == height:
            new_width, new_height = 512, 512
        elif width > height:
            new_width, new_height = 512, int(height * (512.0 / width))
        elif width < height:
            new_width, new_height = int(width * (512.0 / height)), 512

        pdb.gimp_image_scale(image, new_width, new_height)

    if canvas_increase:
        width, height = image.width, image.height

        width_increase = int(width * (canvas_increase / 100))
        height_increase = int(height * (canvas_increase / 100))

        pdb.gimp_image_resize(image,
                              width + width_increase,
                              height + height_increase,
                              int(width_increase / 2),
                              int(height_increase / 2))

        pdb.gimp_layer_resize_to_image_size(current_layer)

    duplicate_layer()

    # alpha to selection
    pdb.gimp_image_select_item(image, 0, current_layer)

    pdb.gimp_selection_grow(image, inner_grow)
    fill_bg()

    second_layer = duplicate_layer()

    pdb.gimp_selection_grow(image, outer_grow)
    fill_fg()

    if shadow:
        duplicate_layer()

        fill_black()

        current_layer.translate(8, 8)

        pdb.gimp_selection_all(image)
        pdb.plug_in_gauss(image, current_layer, 20, 20, 0)
        pdb.gimp_layer_set_opacity(current_layer, 70)

    pdb.gimp_image_merge_down(image, second_layer, 0)

    if shadow:
        pdb.gimp_image_merge_down(image, image.active_layer, 0)

    pdb.gimp_layer_set_name(image.active_layer, "Sticker bordure")

    pdb.gimp_selection_none(image)

    pdb.gimp_image_undo_group_end(image)
    pdb.gimp_context_pop()

    pdb.gimp_displays_flush()


gimpfu.register(
    "python_stickerify_bordure",
    "Put a sticker bordure arround the current layer",
    "Put a sticker bordure arround the current layer",
    "Laurent Peuch",
    "Laurent Peuch",
    "2018",
    "<Image>/Filters/Artistic/Stickerify",
    "",
    [
        (gimpfu.PF_TOGGLE, "resize", "Resize/fit into 512x512", False),
        (gimpfu.PF_ADJUSTMENT, "inner_grow", "Size of inner bordure (px)", 3, (0, 200, 1, 3, 0, 0)),
        (gimpfu.PF_ADJUSTMENT, "outer_grow", "Size of outer bordure (px)", 12, (0, 200, 1, 3, 0, 0)),
        (gimpfu.PF_COLOUR, "border_color_fg", "Color of the outer border", (1.0, 1.0, 1.0)),
        (gimpfu.PF_COLOUR, "border_color_bg", "Color of the inner border", (0.0, 0.0, 0.0)),
        (gimpfu.PF_TOGGLE, "shadow", "Display shadow", True),
        (gimpfu.PF_ADJUSTMENT, "canvas_increase", "Increase canvas size (in %)", 0, (0, 100, 1, 3, 0, 0)),
    ],
    [],
    stickerify_bordure,
)

gimpfu.main()

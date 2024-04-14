from PySide6.QtWidgets import QFileDialog, QMessageBox, QCheckBox
from PySide6.QtCore import QFileInfo
import os.path


class Extractor:
    @classmethod
    def get_embed_file_vfs_path(cls, embed_file, file_tree_item, ui_obj):
        if not embed_file.parent.parent and file_tree_item.parent() == ui_obj.treeItems[0]:
            """ Check for files in top-level directories/trees """
            return True

        next_tree_parent = file_tree_item.parent()
        next_embed_parent = embed_file.parent
        while next_tree_parent and next_embed_parent:
            if next_tree_parent.text(0) != next_embed_parent.name:
                return False
            else:
                next_tree_parent = next_tree_parent.parent()
                next_embed_parent = next_embed_parent.parent

        return True

    @classmethod
    def extractSelected(cls, extract_files, ui_obj):
        if len(extract_files) > 10:
            pass
        # TODO: spawn "Are you sure you want to extract N items?" popup

        try:
            target_dir_info = QFileInfo(cls.spawnTargetPathPrompt(ui_obj) + '/')
            target_path = target_dir_info.absolutePath()
        except IndexError:
            return

        extract_objects = []
        for file_entry in extract_files:
            candidates = ui_obj.archive.root.search(file_entry.text(0)).values()
            for candidate in candidates:
                if cls.get_embed_file_vfs_path(candidate, file_entry, ui_obj):
                    extract_objects.append(candidate)

        multiple_files = len(extract_objects) > 1
        skip_if_it_overwrites = False
        overwrite_all = False
        for obj in extract_objects:
            target_filepath = os.path.join(target_path, obj.name)
            if os.path.isfile(target_filepath) and skip_if_it_overwrites:
                continue

            if os.path.isfile(target_filepath):
                if not overwrite_all:
                    user_response = cls.overwriteFilePrompt(obj.name, target_path, multiple_files)

                    match user_response:
                        case 16384:     # Yes, overwrite this file (will just continue executing)
                            pass
                        case 32768:     # Yes, overwrite all
                            overwrite_all = True
                        case 131072:    # No, skip overwrites
                            skip_if_it_overwrites = True
                        case 4194304:   # User cancelled, escape the loop
                            break
                        case _:         # No, don't overwrite this file (go back to the loop)
                            continue

            obj.extract(out_path=target_path)
            print(f'Extracted {obj.name} to {target_path}')

    # TODO: 'extract right here' and 'extract by path ./xxx/yyy/etc' should be separate options in the GUI

    @classmethod
    def spawnTargetPathPrompt(cls, ui_obj):
        openDialog = QFileDialog(ui_obj)
        openDialog.setAcceptMode(QFileDialog.AcceptSave)
        openDialog.setViewMode(QFileDialog.Detail)
        openDialog.setOption(QFileDialog.DontUseNativeDialog)
        openDialog.setNameFilter('Extract to...')

        try:
            selected = openDialog.getExistingDirectory()
        except IndexError:
            raise IndexError
        else:
            return selected

    @classmethod
    def overwriteFilePrompt(cls, filename, target_dir_name, are_multiple_files):
        prompt = QMessageBox()
        prompt.setText(f'File {filename} already exists in folder {target_dir_name}. Overwrite it?')

        yes_button = prompt.addButton(QMessageBox.StandardButton.Yes)
        yes_button.setText('Overwrite')
        no_button = prompt.addButton(QMessageBox.StandardButton.No)
        no_button.setText('Skip overwriting')
        prompt.setDefaultButton(no_button)
        prompt.addButton(QMessageBox.StandardButton.Cancel)

        if are_multiple_files:
            apply_to_all = QCheckBox()
            apply_to_all.setText('Apply to all')
            prompt.setCheckBox(apply_to_all)

        response = prompt.exec()
        print(response)
        return response

from ckeditor.widgets import CKEditorWidget
from .models import CustomFont
from django.conf import settings

class DynamicCKEditorWidget(CKEditorWidget):
    """
    Custom CKEditor widget that dynamically loads fonts from the database.
    This ensures custom fonts appear in the font dropdown immediately after being added.
    """
    
    def __init__(self, config_name='default', *args, **kwargs):
        super().__init__(config_name=config_name, *args, **kwargs)
        
    def render(self, name, value, attrs=None, renderer=None):
        # Get custom fonts from database
        custom_fonts = CustomFont.objects.all()
        
        # Build font_names string in CKEditor format: "Display Name/CSS Font Name"
        custom_font_list = [
            f"{font.name}/{font.name}" 
            for font in custom_fonts
        ]
        
        # Ensure we have a config dictionary
        if not hasattr(self, 'config'):
            self.config = {}
        
        # Get default fonts from settings
        default_config = settings.CKEDITOR_CONFIGS.get(self.config_name or 'default', {})
        default_fonts = default_config.get('font_names', '')
        
        # Combine custom and default fonts
        # Custom fonts first so they appear at the top of the dropdown
        all_fonts_list = custom_font_list.copy()
        
        # Add default fonts if they exist
        if default_fonts:
            # Split default fonts and filter out empty strings
            default_font_list = [f.strip() for f in default_fonts.split(';') if f.strip()]
            all_fonts_list.extend(default_font_list)
        
        # Join with semicolons
        all_fonts = ';'.join(all_fonts_list)
        
        # Update config with combined fonts
        if all_fonts:
            self.config['font_names'] = all_fonts
        
        return super().render(name, value, attrs, renderer)

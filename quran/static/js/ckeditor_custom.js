(function() {
    'use strict';
    
    // Wait for CKEditor to be fully loaded
    if (typeof CKEDITOR !== 'undefined') {
        
        // Hook into all CKEditor instances when they're ready
        CKEDITOR.on('instanceReady', function(evt) {
            var editor = evt.editor;
            
            console.log('CKEditor instance ready, loading custom fonts...');
            
            // Fetch custom fonts from your Django API
            fetch('/quran/api/fonts/')
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(function(fonts) {
                    console.log('Loaded custom fonts:', fonts);
                    
                    if (fonts && fonts.length > 0) {
                        // Get current font configuration
                        var currentFonts = editor.config.font_names || '';
                        
                        // Build custom font entries in CKEditor format: "Display Name/CSS Font Name"
                        var customFontEntries = fonts.map(function(font) {
                            return font.name + '/' + font.name;
                        });
                        
                        // Combine with semicolons
                        var customFontsString = customFontEntries.join(';');
                        
                        // Prepend custom fonts to existing fonts
                        if (customFontsString) {
                            var newFontNames = customFontsString;
                            if (currentFonts) {
                                newFontNames = customFontsString + ';' + currentFonts;
                            }
                            
                            // Update the configuration
                            editor.config.font_names = newFontNames;
                            
                            console.log('Updated font_names:', editor.config.font_names);
                            
                            // Try to refresh the font dropdown UI
                            // This forces CKEditor to rebuild the combo with new fonts
                            setTimeout(function() {
                                var fontCombo = editor.ui.get('Font');
                                if (fontCombo) {
                                    // Rebuild the dropdown items
                                    var items = editor.config.font_names.split(';');
                                    var newItems = {};
                                    
                                    for (var i = 0; i < items.length; i++) {
                                        var item = items[i].split('/');
                                        if (item.length === 2 && item[0] && item[1]) {
                                            newItems[item[1]] = item[0];
                                        }
                                    }
                                    
                                    // Update the combo items
                                    if (fontCombo._.items) {
                                        fontCombo._.items = newItems;
                                    }
                                    
                                    console.log('Font dropdown refreshed successfully');
                                }
                            }, 100);
                        }
                    } else {
                        console.log('No custom fonts found in database');
                    }
                })
                .catch(function(err) {
                    console.error('Failed to load custom fonts:', err);
                });
        });
        
        console.log('CKEditor custom font loader initialized');
    } else {
        console.warn('CKEDITOR not found, custom fonts will not be loaded');
    }
})();

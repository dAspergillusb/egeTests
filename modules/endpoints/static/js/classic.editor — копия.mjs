import {
        ClassicEditor,
        Essentials,
        Heading,
        List,
        Bold,
        Italic,
        Underline,
        Font,
        Paragraph,
        Subscript,
        Superscript,
        BlockQuote,
        Code,
        Table,
        TableCellProperties,
        TableProperties,
        TableToolbar,
        Alignment,
        SpecialCharacters,
        SpecialCharactersEssentials,
        ImageBlock,
        ImageCaption,
        ImageInline,
        ImageInsert,
        ImageInsertViaUrl,
        ImageResize,
        ImageStyle,
        ImageTextAlternative,
        ImageToolbar,
        ImageUpload,
        AutoImage,
        Autosave,
        Base64UploadAdapter
    } from 'ckeditor5';
    
var Editors = document.querySelectorAll('.ckeditor');

for (var i=0; i<Editors.length; i++) {

    ClassicEditor
        .create( Editors[i], {
            plugins: [ Essentials, Bold, Italic, Underline, Font, Paragraph, Subscript, Superscript, Code, Heading, List,
                      Table, TableCellProperties, TableProperties, TableToolbar, Alignment, BlockQuote, SpecialCharacters, SpecialCharactersEssentials,
                      AutoImage, Autosave, Base64UploadAdapter, ImageBlock, ImageCaption, ImageInline, ImageInsert, ImageInsertViaUrl, ImageResize, 
                      ImageStyle, ImageTextAlternative, ImageToolbar, ImageUpload
            ],
            toolbar: [
                'undo', 'redo', '|', 'heading', 'alignment', '|', 'bold', 'italic', 'underline', '|',
                'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', '|',
                'subscript', 'superscript', 'specialCharacters', 'code', '|', 'bulletedList', 'numberedList', '|', 'insertTable', 'insertImage', 'blockQuote'
            ],
            table: {
                contentToolbar: [ 'tableColumn', 'tableRow', 'mergeTableCells', 'tableProperties', 'tableCellProperties' ]
            },
            image: {
                toolbar: [
                    'toggleImageCaption',
	                'imageTextAlternative',
	                '|',
	                'imageStyle:inline',
	                'imageStyle:wrapText',
	                'imageStyle:breakText',
	                '|',
	                'resizeImage'
                ]
            }
        } )
        .then( ckeditor => {
			window.ckeditor = ckeditor;
		})
        .catch( /* ... */ );
}

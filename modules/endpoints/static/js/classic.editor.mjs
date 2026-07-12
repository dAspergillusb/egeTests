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

let editorInstance = ['editorInstance', 'editorInstanceTwo', 'editorInstanceThree'];
//let editorInstanceTwo = 'editorInstanceTwo';
//let editorInstanceThree = 'editorInstanceThree';

function createClassinEditor(textArea, index) {
}

function loadCKEditor(textArea, index) {
	ClassicEditor
			.create( textArea, {
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
			.then( editor => { window[editorInstance[index]] = editor; } )
			.catch( error => { console.log(error); } );
}

window.loadCKEditor = loadCKEditor;
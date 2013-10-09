
function autocomplete_location(element){
  var autocomplete = new google.maps.places.Autocomplete(
                            element,
                            {
                               types: ['establishment'],
                               componentRestrictions: {country: 'in'},
                         });
  google.maps.event.addListener(autocomplete, 'place_changed',function(){
    $(element).change();
  });
}

$.blueimp.fileupload.prototype.processActions.duplicateImage = function (data, options) {
    if (data.canvas) {
        data.files.push(data.files[data.index]);
    }
    return data;
};
$('#store-logo-image').fileupload({
    processQueue: [
        {
            action: 'loadImage',
            fileTypes: /^image\/(gif|jpeg|png)$/,
            maxFileSize: 20000000 // 20MB
        },
        {
            action: 'resizeImage',
            maxWidth: 1920,
            maxHeight: 1200
        },
        {action: 'saveImage'},
        {action: 'duplicateImage'},
        {
            action: 'resizeImage',
            maxWidth: 1280,
            maxHeight: 1024
        },
        {action: 'saveImage'},
        {action: 'duplicateImage'},
        {
            action: 'resizeImage',
            maxWidth: 1024,
            maxHeight: 768
        },
        {action: 'saveImage'}
    ]
});

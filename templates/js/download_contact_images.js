(function () {
    'use strict'
    var btns_download = document.getElementsByClassName('download_image');

    function download_contact_image() 
    {
        let contact_id = this.id;
        let url = this.value;
        axios({
            url: url, //your url
            method: 'GET',
            responseType: 'blob', // important
        }).then((response) => {
            const url = window.URL.createObjectURL(new Blob([response.data]));
             const link = document.createElement('a');
             link.href = url;
             link.setAttribute('download', contact_id + '.jpg');
             document.body.appendChild(link);
             link.click();
            });
    }

    for(let i=0; i<btns_download.length; i++) {
        let btn =  btns_download[i];
        btn.addEventListener('click', download_contact_image)
    };

})();
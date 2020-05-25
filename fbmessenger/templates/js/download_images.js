(function () {
    'use strict'
    var btns_download = document.getElementsByClassName('btn_download_contact_image');

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
        }).catch(function (error)
        {
            if(error.response.status == 403)
            {
                alert("URL signature might have expired");
                //console.log(error.response);
                // console.log(error.response.status);
                // console.log(error.response.headers);
            }
        });
    }

    for(let i=0; i<btns_download.length; i++) {
        let btn =  btns_download[i];
        btn.addEventListener('click', download_contact_image)
    };

    // Conversations (WIP)
    var btns_download_conversations = document.getElementsByClassName('btn_download_conversation_contact_image');

    function download_contact_conversation_image() 
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
        }).catch(function (error)
        {
            if(error.response.status == 403)
            {
                alert("URL signature might have expired");
                //console.log(error.response);
                // console.log(error.response.status);
                // console.log(error.response.headers);
            }
        });
    }

    for(let i=0; i<btns_download_conversations.length; i++) {
        let btn =  btns_download_conversations[i];
        btn.addEventListener('click', download_contact_conversation_image)
    };

})();
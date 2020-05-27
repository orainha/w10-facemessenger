(function () {
    'use strict'
    //axios.defaults.headers.common['Access-Control-Allow-Origin'] = '*'; // for all requests

    function download() 
    {
        let filename = this.id;
        let url = this.value;
        axios({
            url: url, //your url
            method: 'GET',
            responseType: 'blob', // important
        }).then((response) => {
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            if (filename.search('.mp4')>0)
                link.setAttribute('download', filename);
            else
                link.setAttribute('download', filename + '.jpg');
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
    
    // Contacts
    var btns_download = document.getElementsByClassName('btn_download_contact_image');
    for(let i=0; i<btns_download.length; i++) {
        let btn =  btns_download[i];
        btn.addEventListener('click', download)
    };

    // Conversations
    var btns_download_conversations = document.getElementsByClassName('btn_download_conversation_contact_image');
    for(let i=0; i<btns_download_conversations.length; i++) {
        let btn =  btns_download_conversations[i];
        btn.addEventListener('click', download)
    };

    //Messages
    var btns_download_message_files = document.getElementsByClassName('btn_download_message_file');
    for(let i=0; i<btns_download_message_files.length; i++) {
        let btn =  btns_download_message_files[i];
        btn.addEventListener('click', download)
    };

})();
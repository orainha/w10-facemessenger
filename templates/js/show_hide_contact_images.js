(function () {
    'use strict'
    var btn_show_hide = document.getElementById('show_hide_contact_images');
    btn_show_hide.innerText = 'Show Images';
    var show_images = false
    var first_load = true

    function show_hide_images() {
        
        let image_urls = document.getElementsByClassName('img_url');
        let image_urls_len = image_urls.length;
        let imgs = document.querySelectorAll('img');
        let href_image_urls = document.getElementsByTagName('a');
        //let href_image_urls_len = href_image_urls.length;
        
        if (first_load)
        {
            for (let j=0; j<image_urls_len; j++)
            {
                let ext = '.jpg'
                let contact_id = document.getElementsByTagName('table')[0].rows[j+1].cells[0].innerText;
                let small_image_filename = 'contacts/images/small/' + contact_id + ext;
                let large_image_filename = 'contacts/images/large/' + contact_id + ext;

                let img = document.createElement('img');
                img.setAttribute("src", small_image_filename);
                
                let img_url = image_urls[j];
                img_url.setAttribute("hidden", "true");
                img_url.parentNode.appendChild(img);

                href_image_urls[j].href = large_image_filename;
            }

            first_load = false
        }
        
        show_images = !show_images
        if (show_images)
        {
            imgs.forEach(element => {
                element.removeAttribute("hidden");
            });
            
            for (let j=0; j<image_urls_len; j++)
            {
                image_urls[j].setAttribute("hidden", "true");
            }

            btn_show_hide.innerText = 'Hide Images';
        }
        else
        {
            imgs.forEach(element => {
                element.setAttribute("hidden", "true")
            });

            for (let j=0; j<image_urls_len; j++)
            {
                image_urls[j].removeAttribute("hidden");
                href_image_urls[j].href = href_image_urls[j].innerText;
            }

            btn_show_hide.innerText = 'Show Images';
        }
    }

    btn_show_hide.addEventListener('click', show_hide_images);

})();
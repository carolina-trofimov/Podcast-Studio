


const btns = $('.follow-btn');
    btns.on('click', (evt) => {
      evt.preventDefault();

      const userId = $(evt.target).attr("id");

      const text = $(evt.target).html();
      $.post("/handle-follow", { followed: userId}, (res) =>{
        console.log(res);

        if (text === "Follow") {    
         
          $(evt.target).html("Following"); 
        }

        if (text === "Following") {
          $(evt.target).html("Follow");
        }
      });
      
    });


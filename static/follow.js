


const btns = $('.follow-btn');
    btns.on('click', (evt) => {
      evt.preventDefault();

      const userId = $(evt.target).attr("id");

      const text = $(evt.target).html();
      
      let action = "follow";
      console.log(text);
      if(text === "Following") {
        console.log("it was following")
        action = "unfollow";
      }
      else{
        console.log("it wasn't following");
      }

      $.post("/handle-follow", {followed: userId, action: action}, (res) =>{
        console.log(res);

        if (res.status === "following") {    

          $(evt.target).html("Following"); 
        }
        if (res.status === "unfollowing") {
          $(evt.target).html("Follow");
        }
      });      
    });


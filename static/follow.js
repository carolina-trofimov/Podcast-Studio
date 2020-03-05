

// I want: on click of "follow", bttn text change to "following" and vice-versa
//         I need to capture id of user in session to set on db as follower id and 
//         I need to capture user to be followed id to set on db as followed id


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


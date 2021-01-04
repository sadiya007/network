document.addEventListener('DOMContentLoaded', function() {

    currentFilter = 'profile';
  
    evaluateFollowStatus();
    const buttonFollow = document.querySelector('#buttonFollow');
    if (buttonFollow !== null) {
      buttonFollow.addEventListener('click', (event) => {
        handleFollowClick(event);
      });
    }
  
    loadProfilePosts(profileusername, 'user-posts-view', currentPage);
  
    addPaginationEvents();
  })
  
  function evaluateFollowStatus() {
    // if buttonFollow exists
    const buttonFollow = document.querySelector('#buttonFollow');
    if (buttonFollow !== null) {
      // if i am following this users
      if (buttonFollow.dataset.following === 'True') {
        setButtonToFollowingState(buttonFollow)
      // if i am NOT following
      } else {
        setButtonToNotFollowingState(buttonFollow);
      }
    }
  }
  
  function handleFollowClick(event) {
    const buttonFollow = event.currentTarget;
    if (buttonFollow.dataset.following === 'True') {
      const r1 = new Request(
      `/unfollow/${buttonFollow.dataset.user}`,
      {headers: {'X-CSRFToken': csrftoken}}
      );
      fetch(r1, {
      method: 'POST',
      mode: 'same-origin'
      })
      .then(() => {
        setButtonToNotFollowingState(buttonFollow);
      })
    } else {
      const r2 = new Request(
      `/follow/${buttonFollow.dataset.user}`,
      {headers: {'X-CSRFToken': csrftoken}}
      );
      fetch(r2, {
      method: 'POST',
      mode: 'same-origin'
      })
      .then(() => {
        setButtonToFollowingState(buttonFollow);
      })
    }
    buttonFollow.blur();
  }
  
  function resetButtonFollowEvents(buttonFollow) {
    buttonFollow.removeEventListener('mouseover', handleFollowMouseOver);
    buttonFollow.removeEventListener('mouseout', handleFollowMouseOut);
  }
  
  function setButtonToFollowingState(buttonFollow) {
    resetButtonFollowEvents(buttonFollow);
    // show button text FOLLOWING (filled blue)
    buttonFollow.className = 'btn-sm btn-primary rounded-pill';
    buttonFollow.innerHTML = 'Following';
    buttonFollow.addEventListener('mouseover', handleFollowMouseOver);
    buttonFollow.addEventListener('mouseout', handleFollowMouseOut);
    buttonFollow.dataset.following = 'True';
  }
  
  function setButtonToNotFollowingState(buttonFollow) {
    resetButtonFollowEvents(buttonFollow);
    // show button text FOLLOW (outlined blue)
    buttonFollow.className = 'btn-sm btn-outline-primary rounded-pill';
    buttonFollow.innerHTML = 'Follow';
    buttonFollow.dataset.following = 'False';
  }
  
  function handleFollowMouseOver(event) {
    // show button text UNFOLLOW on mouseover (filled red)
    event.currentTarget.className = 'btn-sm btn-danger rounded-pill';
    event.currentTarget.innerHTML = 'Unfollow';
  }
  
  function handleFollowMouseOut(event) {
    // show button text UNFOLLOW on mouseover (filled red)
    event.currentTarget.className = 'btn-sm btn-primary rounded-pill';
    event.currentTarget.innerHTML = 'Following';
  }
  
  function loadProfilePosts(profile, containerID, page) {
    const currentFilter = profile;
    var postCount;
  
    recreatePostsView();
  
    // Get latests mails from mailbox and render them
    fetch(`/profile/${currentFilter}/${page}`)
    .then(response => response.json())
    .then(data => {
        data.forEach(function(element) {
          addPost(element, containerID);
        });
        postCount = countPosts(data);
        return postCount;
    })
    .then(postCount => {
      evaluatePaginator(postCount);
    });
  }
  
  function recreatePostsView() {
    const postsView = document.querySelector('#user-posts-view');
    clearNode(postsView);
    const headingNode = document.createElement('h3');
    headingNode.innerHTML = 'Latest User Posts';
    postsView.append(headingNode);
  }
const heartSrc = '/static/network/image/heart.png';
const heartSrcOutline = '/static/network/image/heart_outline.png';
const editSrc = '/static/network/image/edit.png';
const postLimit = 10;
var currentPage = 1;
var currentFilter = 'all';
var express = require('express');
var app = express();
app.use(express.static(__dirname + '/image/'));


function addPost(contents, containerId) {
  // create post container
  const post = document.createElement('div');
  post.className = 'container p-3 my-3 border';
  post.setAttribute('id', `post${contents.id}`);

  createPostContent(contents, post)

  // add post to posts_view
  document.querySelector(`#${containerId}`).append(post);
}

function clearNode(node) {
  var children = Array.from(node.children);
  children.forEach((child) => { child.remove(); });
  node.innerHTML = '';
}

function evaluatePaginator(postCount) {
  // Previous link
  // First Page
  if (currentPage === 1) {
    document.querySelector('#previuosListItemPag').classList.add('disabled');
    document.querySelector('#previousLinkPag').setAttribute('tabIndex', '-1');
    document.querySelector('#previousLinkPag').setAttribute('aria-disabled', 'true');
  }
  // Other page
  else {
    document.querySelector('#previuosListItemPag').classList.remove('disabled');
    document.querySelector('#previousLinkPag').removeAttribute('tabIndex');
    document.querySelector('#previousLinkPag').removeAttribute('aria-disabled');
  }

  // Next link
  // No posts
  if (postCount < postLimit) {
    document.querySelector('#nextListItemPag').classList.add('disabled');
    document.querySelector('#nextLinkPag').setAttribute('tabIndex', '-1');
    document.querySelector('#nextLinkPag').setAttribute('aria-disabled', 'true');
  }
  // There are posts
  else {
    document.querySelector('#nextListItemPag').classList.remove('disabled');
    document.querySelector('#nextLinkPag').removeAttribute('tabIndex');
    document.querySelector('#nextLinkPag').removeAttribute('aria-disabled');
  }
}

function countPosts(jsonDataObj) {
  return jsonDataObj.length;
}

function addPaginationEvents() {
  // Next page event
  document.querySelector('#nextLinkPag').addEventListener('click', (event) => {
    let nextPage = currentPage + 1;
    currentPage = nextPage;
    if (currentFilter === 'all') { posts(nextPage); }
    else if (currentFilter === 'following') { following(nextPage); }
    else if (currentFilter === 'profile') { loadProfilePosts(profileusername, 'user-posts-view', nextPage); }
  });

  // Previous page event
  document.querySelector('#previousLinkPag').addEventListener('click', (event) => {
    let previousPage = currentPage - 1;
    currentPage = previousPage;
    if (currentFilter === 'all') { posts(previousPage); }
    else if (currentFilter === 'following') { following(previousPage); }
    else if (currentFilter === 'profile') { loadProfilePosts(profileusername, 'user-posts-view', previousPage); }
  });
}

function handleLikeClick(event, id) {
  const heart = event.currentTarget;
  // if user likes this post
  if (heart.dataset.liking === 'true') {
    fetch(`/unlike/${id}`, {
    method: 'POST',
    headers: {'X-CSRFToken': csrftoken},
    mode: 'same-origin'
    })
    .then(() => {
      const counter = document.querySelector(`#likeCount${id}`)
      counter.innerHTML = parseInt(counter.innerHTML) - 1
      heart.src = heartSrcOutline;
      heart.dataset.liking = 'false';
    });
  //if user doesn't like this post
  } else {
    fetch(`/like/${id}`, {
    method: 'POST',
    headers: {'X-CSRFToken': csrftoken},
    mode: 'same-origin'
    })
    .then(() => {
      const counter = document.querySelector(`#likeCount${id}`)
      counter.innerHTML = parseInt(counter.innerHTML) + 1
      heart.src = heartSrc;
      heart.dataset.liking = 'true'
    });
  }
}

function handleEditClick(event) {
  const postid = `${event.currentTarget.dataset.postid}`
  post = document.querySelector(`#post${postid}`);
  messageElement = document.querySelector(`div[id=post${postid}] small`);
  message = messageElement.innerHTML;
  messageContainer = messageElement.parentElement;
  messageElement.remove();
  event.currentTarget.remove();

  // edit form
  const form = document.createElement('form');
  const formGroup = document.createElement('div');
  formGroup.classList.add('form-group');
  const textInput = document.createElement('textarea');
  textInput.classList.add('form-control');
  textInput.id = 'editPostTextArea';
  textInput.dataset.postid = `${postid}`;
  textInput.value = `${message}`;
  formGroup.append(textInput);
  form.append(formGroup);

  messageContainer.append(form);

  // submit button
  const submit =  document.createElement('button');
  submit.id = 'editPostSubmit'
  submit.type = 'submit';
  submit.classList.add('btn');
  submit.classList.add('btn-primary');
  submit.classList.add('btn-sm');
  submit.dataset.postid = `${postid}`;
  submit.innerHTML = 'Save';
  submit.addEventListener('click', (event) => {
    handleEditPostSubmitClick(event);
  });

  messageContainer.append(submit);

  textInput.focus();
}

function handleEditPostSubmitClick(event) {
  const postid = `${event.currentTarget.dataset.postid}`;
  message = document.querySelector(`textarea[data-postid="${postid}"]`).value;
  fetch(`/editPost/${postid}`, {
  method: 'POST',
  headers: {'X-CSRFToken': csrftoken},
  mode: 'same-origin',
  body: JSON.stringify({
      message: message
    })
  })
  .then(response => response.json())
  .then(result => {
    const post = document.querySelector(`div#post${postid}`);
    clearNode(post);
    createPostContent(result, post);
  })
  .catch((error) => {
    console.error('Error!:', error);
    alert(error);
  });
}

function createPostContent(contents, post) {
  // create user link
  const link = document.createElement('a');
  link.className = 'usernameLinkPost';
  link.href = '/profile/' + contents.user.username;
  post.append(link);
  // create user text
  const userText = document.createElement('strong');
  userText.innerHTML = contents.user.username;
  link.append(userText);
  // line break
  post.append(document.createElement('br'));
  // create message
  const messageContainer = document.createElement('div');
  const message = document.createElement('small');
  message.innerHTML = contents.message;
  messageContainer.append(message);

  // edit link
  if ((document.querySelector('#userNavItem')) && (contents.user.username === username)) {
    const editImg = document.createElement('img');
    editImg.id = 'editPost';
    editImg.src = editSrc;
    editImg.dataset.postid = contents.id;
    // set pointer behaviour
    editImg.addEventListener('mouseover', () => {
      editImg.style.cursor = 'pointer';
    });
    editImg.addEventListener('mouseout', () => {
      editImg.style.cursor = 'auto';
    });
    editImg.addEventListener('click', (event) => {
      handleEditClick(event);
    })
    messageContainer.append(editImg);
  }
  post.append(messageContainer);

  // create timestamped
  const timestampSmall = document.createElement('small');
  const timestampItalic = document.createElement('i');
  timestampItalic.innerHTML = contents.created_at;
  timestampSmall.append(timestampItalic);
  post.append(timestampSmall);
  // line break
  post.append(document.createElement('br'));
  // create like bar
  const imageHeart = document.createElement('img');
  imageHeart.id = 'postLikesheart';
  // If user is NOT authenticated
  if (!document.querySelector('#userNavItem')) {
    imageHeart.src = heartSrcOutline;
  // If user IS authenticated
  } else {
    // lookup if user is likes this post
    fetch(`/like/${contents.id}`)
    .then(response => response.json())
    .then(result => {
      if (result.message === 'true') {
        imageHeart.src = heartSrc;
        imageHeart.dataset.liking = true;
      } else {
        imageHeart.src = heartSrcOutline;
        imageHeart.dataset.liking = false;
      }

    //if it is not my posts
    if (contents.user.username !== username) {
      // set pointer behaviour
      imageHeart.addEventListener('mouseover', () => {
        imageHeart.style.cursor = 'pointer';
      });
      imageHeart.addEventListener('mouseout', () => {
        imageHeart.style.cursor = 'auto';
      });
      imageHeart.addEventListener('click', (event) => {
        handleLikeClick(event, contents.id);
      });
    }
  });
  }

  post.append(imageHeart);
  const likeCount = document.createElement('small');
  likeCount.innerHTML = contents.likes;
  likeCount.id = 'likeCount'+ contents.id;
  post.append(document.createTextNode("\u00A0"));
  post.append(likeCount);
}
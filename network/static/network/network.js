document.addEventListener('DOMContentLoaded', function() {

    document.querySelector('#posts-view').style.display = 'block';
    document.querySelector('#new-post-view').style.display = 'none';
  
    // All posts event
    document.querySelector('#posts-link').addEventListener('click', (e) => {
      posts(1);
    });
  
    // All posts event
    const allPostsLink = document.querySelector('#allPosts')
    if (allPostsLink) {
      allPostsLink.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelector('#allPostsLabel').classList.add('active');
        document.querySelector('#followingPostsLabel').classList.remove('active');
        posts(1);
      });
    }
  
    // Following posts event
    const followingLink = document.querySelector('#followingPosts');
    if (followingLink) {
      followingLink.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelector('#allPostsLabel').classList.remove('active');
        document.querySelector('#followingPostsLabel').classList.add('active');
        following(1);
      });
    }
  
    // New post event
    const newPostLink = document.querySelector('#new-post-link');
    if (newPostLink) {
      newPostLink.addEventListener('click', (e) => {
        e.preventDefault();
        new_post();
      });
    }
  
    addPaginationEvents();
  
    // The first page from all posts
    posts(1);
  });
  
  function new_post() {
    const postsView = document.querySelector('#posts-view');
    clearNode(postsView);
    postsView.style.display = 'none';
    document.querySelector('#posts-selector').style.display = 'none';
    document.querySelector('#paginatorNav').style.display = 'none';
    document.querySelector('#new-post-view').style.display = 'block';
  }
  
  function posts(page) {
    const currentFilter = 'all';
    var postCount;
  
    recreatePostsView();
    document.querySelector('#posts-view').style.display = 'block';
    document.querySelector('#paginatorNav').style.display = 'block';
    document.querySelector('#new-post-view').style.display = 'none';
  
    // Get latests mails from mailbox and render them
    fetch(`/posts/${currentFilter}/${page}`)
    .then(response => response.json())
    .then(data => {
        data.forEach(function(element) {
          addPost(element, 'posts-view');
        });
        postCount = countPosts(data);
        return postCount;
    })
    .then(postCount => {
      evaluatePaginator(postCount);
    });
  }
  
  function following(page) {
    const currentFilter = 'following';
    var postCount;
  
    recreatePostsView();
    document.querySelector('#posts-view').style.display = 'block';
    document.querySelector('#paginatorNav').style.display = 'block';
    document.querySelector('#new-post-view').style.display = 'none';
  
    // Get latests mails from mailbox and render them
    fetch(`/posts/${currentFilter}/${page}`)
    .then(response => response.json())
    .then(data => {
        data.forEach(function(element) {
          addPost(element, 'posts-view');
        });
        postCount = countPosts(data);
        return postCount;
    })
    .then(postCount => {
      evaluatePaginator(postCount);
    });
  }
  
  function recreatePostsView() {
    const postsView = document.querySelector('#posts-view');
    clearNode(postsView);
    const headingNode = document.createElement('h3');
    headingNode.innerHTML = 'Latest Posts';
    postsView.append(headingNode);
  }
  
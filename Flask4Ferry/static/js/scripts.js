document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('ferriesSubMenu').style.display = 'none'; // Initially hide Ferries submenu
  // Initialize event listeners
  document.getElementById('addPromotionBtn').addEventListener('click', showAddPromotion);
  document.getElementById('modifyPromotionBtn').addEventListener('click', showModifyPromotionOptions);
  document.getElementById('deletePromotionBtn').addEventListener('click', showDeletePromotionOptions);
  document.getElementById('viewPromotionsBtn').addEventListener('click', showPromotions);

  document.getElementById('promotionForm').addEventListener('submit', (e) => {
    e.preventDefault();
    addNewPromotion();
  });

  document.getElementById('modifyForm').addEventListener('submit', (e) => {
    e.preventDefault();
    saveModifiedPromotion();
  });
});

function toggleSubMenu() {
  const submenu = document.getElementById('submenu');
  submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
}

function showAddPromotion() {
  hideAllSections();
  document.getElementById('promotionForm').style.display = 'flex';
}

function showModifyPromotionOptions() {
  hideAllSections();
  document.getElementById('codeList').style.display = 'flex';

  fetch('/promotions')
    .then(response => response.json())
    .then(data => {
      const codeList = document.getElementById('codeList');
      codeList.innerHTML = '<h2>Select a Promotion to Modify</h2>';

      data.promotions.forEach(promotion => {
        const button = document.createElement('button');
        button.textContent = promotion.code;
        button.addEventListener('click', () => showModifyPromotionForm(promotion));
        codeList.appendChild(button);
      });
    })
    .catch(error => console.error('Error:', error));
}

function showModifyPromotionForm(promotion) {
  hideAllSections();
  document.getElementById('modifyForm').style.display = 'flex';

  document.getElementById('modifyTitle').value = promotion.title;
  document.getElementById('modifyCode').value = promotion.code;
  document.getElementById('modifyFromDate').value = promotion.from_date;
  document.getElementById('modifyToDate').value = promotion.to_date;
  document.getElementById('modifyPercentage').value = promotion.percentage;
}

function saveModifiedPromotion() {
  const promotionData = {
    title: document.getElementById('modifyTitle').value,
    code: document.getElementById('modifyCode').value,
    from_date: document.getElementById('modifyFromDate').value,
    to_date: document.getElementById('modifyToDate').value,
    percentage: document.getElementById('modifyPercentage').value,
  };

  fetch(`/modify_promotion/${promotionData.code}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(promotionData)
  })
    .then(response => response.json())
    .then(data => {
      alert(data.message);
      hideAllSections();
    })
    .catch(error => console.error('Error:', error));
}

function showDeletePromotionOptions() {
  hideAllSections();
  document.getElementById('codeList').style.display = 'flex';

  fetch('/promotions')
    .then(response => response.json())
    .then(data => {
      const codeList = document.getElementById('codeList');
      codeList.innerHTML = '<h2>Select a Promotion to Delete</h2>';

      data.promotions.forEach(promotion => {
        const button = document.createElement('button');
        button.textContent = promotion.code;
        button.addEventListener('click', () => deletePromotion(promotion.code));
        codeList.appendChild(button);
      });
    })
    .catch(error => console.error('Error:', error));
}

function deletePromotion(code) {
  if (confirm('Are you sure you want to delete this promotion?')) {
    fetch(`/delete_promotion/${code}`, {
      method: 'DELETE'
    })
      .then(response => response.json())
      .then(data => {
        alert(data.message);
        hideAllSections();
      })
      .catch(error => console.error('Error:', error));
  }
}

function showPromotions() {
  hideAllSections();
  document.getElementById('promotions').style.display = 'block';

  fetch('/view_promotions')
    .then(response => response.text())
    .then(html => {
      document.getElementById('promotions').innerHTML = html;
    })
    .catch(error => console.error('Error:', error));
}

function addNewPromotion() {
  const promotionData = {
    title: document.getElementById('promotionTitle').value,
    code: document.getElementById('promotionCode').value,
    from_date: document.getElementById('fromDate').value,
    to_date: document.getElementById('toDate').value,
    percentage: document.getElementById('percentage').value,
  };

  fetch('/add_promotion', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(promotionData)
  })
    .then(response => response.json())
    .then(data => {
      alert(data.message);
      hideAllSections();
    })
    .catch(error => console.error('Error:', error));
}

function hideAllSections() {
  document.getElementById('promotionForm').style.display = 'none';
  document.getElementById('codeList').style.display = 'none';
  document.getElementById('promotions').style.display = 'none';
  document.getElementById('modifyForm').style.display = 'none';
}



function toggleFerriesSubMenu() {
  const submenu = document.getElementById('ferriesSubMenu');
  submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
}

function showAddFerry() {
  hideAllSections();
  // Display the form for adding a ferry (needs to be defined in your HTML)
  document.getElementById('addFerryForm').style.display = 'flex';
}

function showModifyFerry() {
  hideAllSections();
  // Display the form for modifying a ferry (needs to be defined in your HTML)
  document.getElementById('modifyFerryForm').style.display = 'flex';
}

function showDeleteFerry() {
  hideAllSections();
  // Display the form for deleting a ferry (needs to be defined in your HTML)
  document.getElementById('deleteFerryForm').style.display = 'flex';
}



document.addEventListener('DOMContentLoaded', async () => {
  const params = new URLSearchParams(window.location.search);
  const referralSource = params.get('ref') || 'Direct';
  const cleanRef = referralSource.replace(/\s+/g, '').toUpperCase();
  
  const offersListContainer = document.getElementById('offers-list');
  offersListContainer.innerHTML = `<p>Loading offers...</p>`;
  
  function getRedeemedOffers() {
    return JSON.parse(localStorage.getItem('redeemedCommunityOffers')) || {};
  }
  function markOfferAsRedeemed(offerId) {
    const redeemed = getRedeemedOffers();
    redeemed[offerId] = true;
    localStorage.setItem('redeemedCommunityOffers', JSON.stringify(redeemed));
  }
  
  try {
    const response = await fetch(`/api/get-offers?ref=${encodeURIComponent(referralSource)}`);
    if (!response.ok) throw new Error(`API Error: ${response.status}`);
    const offers = await response.json();
    
    offersListContainer.innerHTML = '';
    const redeemedOffers = getRedeemedOffers();
  
    offers.forEach(offer => {
      const isRedeemed = redeemedOffers[offer.OfferID] || false;
      const dynamicDiscountCode = `${offer.CodePrefix}-${cleanRef}`;
      const card = document.createElement('div');
      card.className = 'offer-card' + (isRedeemed ? ' redeemed' : '');
      card.id = `offer-${offer.OfferID}`;
      card.innerHTML = `
        <h3>${offer.Merchant}</h3>
        <p>${offer.Description}</p>
        <div class="offer-code">Use Code: ${dynamicDiscountCode}</div>
        ${isRedeemed 
          ? `<p class="redeemed-text">Already redeemed on this device</p>`
          : `<button class="redeem-btn" data-offer-id="${offer.OfferID}">Merchant: Tap to Redeem</button>`}
      `;
      offersListContainer.appendChild(card);
    });
  
    offersListContainer.addEventListener('click', async (event) => {
      if (event.target.classList.contains('redeem-btn')) {
        const button = event.target;
        const offerId = button.dataset.offerId;
        button.disabled = true;
        button.textContent = 'Redeeming...';
  
        try {
          const resp = await fetch('/api/redeem-offer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ offerId, refCode: referralSource })
          });
          if (!resp.ok) throw new Error(`API Error: ${resp.status}`);
          
          markOfferAsRedeemed(offerId);
          
          const card = document.getElementById(`offer-${offerId}`);
          card.classList.add('redeemed');
          button.remove();
          
          const msg = document.createElement('p');
          msg.className = 'redeemed-text';
          msg.textContent = 'Offer Redeemed!';
          card.appendChild(msg);
        } catch (err) {
          button.disabled = false;
          button.textContent = 'Merchant: Tap to Redeem';
          alert('Error redeeming offer. Please check your connection and try again.');
        }
      }
    });
  
  } catch (error) {
    console.error('Failed to load offers:', error);
    offersListContainer.innerHTML = `<p style="color: red; text-align: center;">Error loading offers. Please ensure the API is running and configured correctly.</p>`;
  }
});
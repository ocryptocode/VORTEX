// VORTEX Village Frontend Integration
// This file handles the connection between the 3D frontend and Python backend

class VortexVillageAPI {
    constructor() {
        this.baseURL = 'http://localhost:8000'; // Adjust based on your backend
        this.endpoints = {
            presales: '/api/presales',
            events: '/api/events',
            collabs: '/api/collabs',
            dao: '/api/dao',
            wallet: '/api/wallet'
        };
    }

    // Fetch live presales data
    async getPresales() {
        try {
            const response = await fetch(`${this.baseURL}${this.endpoints.presales}`);
            const data = await response.json();
            this.updatePresalesUI(data);
        } catch (error) {
            console.error('Error fetching presales:', error);
        }
    }

    // Fetch upcoming events
    async getEvents() {
        try {
            const response = await fetch(`${this.baseURL}${this.endpoints.events}`);
            const data = await response.json();
            this.updateEventsUI(data);
        } catch (error) {
            console.error('Error fetching events:', error);
        }
    }

    // Fetch collaboration data
    async getCollabs() {
        try {
            const response = await fetch(`${this.baseURL}${this.endpoints.collabs}`);
            const data = await response.json();
            this.updateCollabsUI(data);
        } catch (error) {
            console.error('Error fetching collabs:', error);
        }
    }

    // Fetch DAO data
    async getDAOData() {
        try {
            const response = await fetch(`${this.baseURL}${this.endpoints.dao}`);
            const data = await response.json();
            this.updateDAOUI(data);
        } catch (error) {
            console.error('Error fetching DAO data:', error);
        }
    }

    // Update presales UI with real data
    updatePresalesUI(presales) {
        const presalesGrid = document.querySelector('.presales-grid');
        if (!presalesGrid) return;

        presalesGrid.innerHTML = '';
        
        presales.forEach(presale => {
            const presaleCard = document.createElement('div');
            presaleCard.className = 'presale-card';
            presaleCard.innerHTML = `
                <div class="presale-header">
                    <img src="${presale.logo || 'https://via.placeholder.com/60x60/4a90e2/ffffff?text=PROJ'}" 
                         alt="${presale.name}" class="presale-logo">
                    <div class="presale-info">
                        <h3>${presale.name}</h3>
                        <p>${presale.description}</p>
                    </div>
                </div>
                <div class="presale-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${presale.progress}%"></div>
                    </div>
                    <span class="progress-text">${presale.progress}% Complete</span>
                </div>
                <div class="presale-details">
                    <div class="detail">
                        <span>Price:</span>
                        <span>$${presale.price}</span>
                    </div>
                    <div class="detail">
                        <span>Raised:</span>
                        <span>$${presale.raised}K / $${presale.target}K</span>
                    </div>
                </div>
                <button class="btn btn-primary" onclick="vortexAPI.participateInPresale('${presale.id}')">
                    Participate
                </button>
            `;
            presalesGrid.appendChild(presaleCard);
        });
    }

    // Update events UI with real data
    updateEventsUI(events) {
        const eventsTimeline = document.querySelector('.events-timeline');
        if (!eventsTimeline) return;

        eventsTimeline.innerHTML = '';
        
        events.forEach(event => {
            const eventItem = document.createElement('div');
            eventItem.className = 'event-item';
            
            const eventDate = new Date(event.date);
            const day = eventDate.getDate();
            const month = eventDate.toLocaleDateString('en-US', { month: 'short' }).toUpperCase();
            
            eventItem.innerHTML = `
                <div class="event-date">
                    <span class="day">${day}</span>
                    <span class="month">${month}</span>
                </div>
                <div class="event-content">
                    <h3>${event.title}</h3>
                    <p>${event.description}</p>
                    <span class="event-time">${event.time}</span>
                </div>
            `;
            eventsTimeline.appendChild(eventItem);
        });
    }

    // Update collabs UI with real data
    updateCollabsUI(collabs) {
        const collabsGrid = document.querySelector('.collabs-grid');
        if (!collabsGrid) return;

        collabsGrid.innerHTML = '';
        
        collabs.forEach(collab => {
            const collabCard = document.createElement('div');
            collabCard.className = 'collab-card';
            collabCard.innerHTML = `
                <img src="${collab.logo || 'https://via.placeholder.com/120x60/4ecdc4/ffffff?text=PARTNER'}" 
                     alt="${collab.name}" class="collab-logo">
                <h3>${collab.name}</h3>
                <p>${collab.description}</p>
            `;
            collabsGrid.appendChild(collabCard);
        });
    }

    // Update DAO UI with real data
    updateDAOUI(daoData) {
        // Update DAO stats
        const daoNumbers = document.querySelectorAll('.dao-number');
        if (daoNumbers.length >= 3) {
            daoNumbers[0].textContent = daoData.holders.toLocaleString();
            daoNumbers[1].textContent = daoData.activeProposals;
            daoNumbers[2].textContent = `${daoData.participationRate}%`;
        }

        // Update proposals
        const proposals = document.querySelector('.proposals');
        if (proposals && daoData.proposals) {
            const proposalsList = proposals.querySelector('.proposal-item');
            if (proposalsList) {
                proposalsList.innerHTML = '';
                daoData.proposals.forEach(proposal => {
                    const proposalItem = document.createElement('div');
                    proposalItem.className = 'proposal-item';
                    proposalItem.innerHTML = `
                        <h4>${proposal.title}</h4>
                        <div class="proposal-votes">
                            <span class="vote-yes">Yes: ${proposal.yesVotes}</span>
                            <span class="vote-no">No: ${proposal.noVotes}</span>
                        </div>
                    `;
                    proposalsList.appendChild(proposalItem);
                });
            }
        }
    }

    // Participate in presale
    async participateInPresale(presaleId) {
        try {
            const response = await fetch(`${this.baseURL}${this.endpoints.presales}/${presaleId}/participate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    amount: 100, // This would come from user input
                    wallet: 'user_wallet_address' // This would come from wallet connection
                })
            });
            
            const result = await response.json();
            if (result.success) {
                alert('Successfully participated in presale!');
                this.getPresales(); // Refresh presales data
            } else {
                alert('Error participating in presale: ' + result.error);
            }
        } catch (error) {
            console.error('Error participating in presale:', error);
            alert('Error participating in presale. Please try again.');
        }
    }

    // Initialize API and load data
    async init() {
        console.log('Initializing VORTEX Village API...');
        
        // Load all data
        await Promise.all([
            this.getPresales(),
            this.getEvents(),
            this.getCollabs(),
            this.getDAOData()
        ]);
        
        console.log('VORTEX Village API initialized successfully!');
    }
}

// Initialize the API when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.vortexAPI = new VortexVillageAPI();
    window.vortexAPI.init();
});

// Export for use in other modules
export default VortexVillageAPI;
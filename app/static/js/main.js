// main.js - Noxco Instagram Stijl (Gecentraliseerde en werkende versie)

document.addEventListener('DOMContentLoaded', function () {
    // --- Drag & drop upload (uploadpagina) ---
    const uploadArea = document.getElementById('uploadArea');
    const stlInput = document.getElementById('stlFile');
    const preview = document.getElementById('uploadPreview');
    const previewImg = document.getElementById('filePreviewImage');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');

    if (uploadArea && stlInput) {
        uploadArea.addEventListener('click', () => stlInput.click());
        uploadArea.addEventListener('dragover', e => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        uploadArea.addEventListener('dragleave', e => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        uploadArea.addEventListener('drop', e => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files.length) {
                stlInput.files = e.dataTransfer.files;
                showUploadPreview(e.dataTransfer.files[0]);
            }
        });
        stlInput.addEventListener('change', function () {
            if (this.files.length) {
                showUploadPreview(this.files[0]);
            }
        });

        function showUploadPreview(file) {
            if (file && file.type.startsWith('image/')) {
                let reader = new FileReader();
                reader.onload = e => previewImg.src = e.target.result;
                reader.readAsDataURL(file);
                preview.style.display = '';
            } else {
                previewImg.src = '';
                preview.style.display = 'none';
            }
            fileName.innerText = file.name;
            fileSize.innerText = (file.size / 1024).toFixed(1) + ' KB';
        }

        // "Bladeren" tekst klikbaar maken
        let browse = uploadArea.querySelector('.browse-files');
        if (browse) browse.addEventListener('click', e => {
            e.stopPropagation();
            stlInput.click();
        });
    }

    // --- Profielfoto preview bij upload (profiel bewerken) ---
    let picInput = document.getElementById('profile_picture_upload');
    let previewPic = document.getElementById('currentProfilePic');
    if (picInput && previewPic) {
        picInput.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                let reader = new FileReader();
                reader.onload = e => previewPic.src = e.target.result;
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // --- Klikbare modelkaarten: redirect naar detailpagina ---
    document.querySelectorAll('.clickable-model-item, .profile-gallery-item').forEach(card => {
        card.addEventListener('click', function (event) {
            // Voorkom omleiding als er op een link binnen de kaart is geklikt
            if (event.target.tagName === 'A' || event.target.closest('a')) {
                return;
            }
            let modelId = card.dataset.modelId;
            if (modelId) {
                window.location.href = "/model/" + modelId;
            }
        });
    });

    // --- "Model uploaden" knop ---
    const openUploadBtn = document.getElementById('openUploadModalBtn');
    if (openUploadBtn) {
        openUploadBtn.addEventListener('click', function() {
            // Haal de URL uit het data-attribuut van de knop (opgelost voor url_for)
            const uploadUrl = this.dataset.uploadUrl; // DIT MOET IN JE HTML ZIJN INGESTELD!
            if (uploadUrl) {
                window.location.href = uploadUrl;
            } else {
                console.error("Data-upload-url attribuut niet gevonden op openUploadModalBtn. Zorg ervoor dat het in HTML is toegevoegd.");
            }
        });
    }

    // --- Klikafhandeling voor bericht-items (indien van toepassing) ---
    document.querySelectorAll('.bericht-item').forEach(item => {
        item.addEventListener('click', () => {
            const berichtId = item.dataset.berichtId;
            if (berichtId) {
                window.location.href = `/bericht/${berichtId}`;
            }
        });
    });

    // --- Klikafhandeling voor vriend-items (indien van toepassing) ---
    document.querySelectorAll('.friend-item').forEach(item => {
        item.addEventListener('click', (event) => {
            // Voorkom omleiding als er op een link binnen het vriend-item is geklikt
            if (event.target.tagName === 'A' || event.closest('a')) {
                return;
            }
            const friendId = item.dataset.friendId;
            if (friendId) {
                window.location.href = `/profile/${friendId}`;
            }
        });
    });

    // --- Universeel fade-in-on-scroll animatie-effect ---
    function setupFadeInOnScroll() {
        const fadeInElements = document.querySelectorAll('.fade-in-on-scroll');
        if (fadeInElements.length > 0) {
            const observer = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                rootMargin: '0px',
                threshold: 0.1
            });
            fadeInElements.forEach(element => observer.observe(element));
        }
    }
    setupFadeInOnScroll();

    // --- Algemene "Terug"-knop afhandeling ---
    document.querySelectorAll('.terug-btn').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            window.history.back();
        });
    });


    // --- TABBLAD LOGICA VOOR PROFIELPAGINA ---
    // Deze logica is nu hier gecentraliseerd.
    const tabButtons = document.querySelectorAll('.profile-tabs .tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    if (tabButtons.length > 0 && tabContents.length > 0) {
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Verwijder 'active' klasse van alle knoppen en verberg alle inhoud
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.style.display = 'none');

                // Voeg 'active' klasse toe aan de geklikte knop
                this.classList.add('active');

                // Toon de juiste inhoud op basis van de data-tab attribuut
                const targetTab = this.dataset.tab;
                const targetContent = document.getElementById(targetTab + '-tab-content');
                if (targetContent) {
                    // GEBRUIK HIER DE CORRECTE DISPLAY STIJLEN: flex voor 'friends', grid voor 'posts'
                    targetContent.style.display = (targetTab === 'friends') ? 'flex' : 'grid';
                }
            });
        });

        // Activeer de standaardtab ("Berichten") bij het laden van de pagina
        const defaultTabButton = document.querySelector('.profile-tabs .tab-button[data-tab="posts"]');
        if (defaultTabButton) {
            defaultTabButton.click(); // Simuleer een klik om de initiële weergave in te stellen
        }
    }


    // --- CODE OM STL-VIEWERS TE INITIALISEREN OP DE PROFIELPAGINA ---
    // Dit vereist dat Three.js en STLLoader.js zijn geladen VOOR main.js (in base.html)
    const stlViewerPlaceholders = document.querySelectorAll('.stl-viewer-placeholder');

    if (stlViewerPlaceholders.length > 0) {
        stlViewerPlaceholders.forEach(placeholder => {
            const modelId = placeholder.id.replace('stl-viewer-profile-', ''); // Haal model ID op
            const galleryItem = placeholder.closest('.profile-gallery-item');
            const filename = galleryItem ? galleryItem.dataset.filename : null; // Haal filename uit data-attribuut

            // Controleer of Three.js en STLLoader beschikbaar zijn
            if (filename && typeof THREE !== 'undefined' && typeof THREE.STLLoader !== 'undefined') {
                initStlViewer(placeholder.id, filename);
            } else {
                console.warn(`Kan viewer niet initialiseren voor model ID ${modelId}. Bestandsnaam, Three.js of STLLoader ontbreekt.`);
            }
        });
    }

    // Functie om één STL-viewer te initialiseren
    function initStlViewer(containerId, stlFilename) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container met ID ${containerId} niet gevonden.`);
            return;
        }

        // Basis Three.js instellingen
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xf3f3f3); // Lichte achtergrond

        const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
        camera.position.z = 5;

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        // Licht toevoegen
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
        scene.add(ambientLight);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(1, 1, 1).normalize();
        scene.add(directionalLight);

        // STLLoader initialiseren en model laden
        const loader = new THREE.STLLoader();
        // Belangrijk: het pad naar het STL-bestand. Dit moet overeenkomen met je Flask route.
        // Dit URL moet door Flask geserveerd worden, bijvoorbeeld via /static/uploads/stl_models/
        const stlPath = `/static/uploads/stl_models/${stlFilename}`; // Pas dit aan indien nodig!

        loader.load(stlPath, function (geometry) {
            geometry.computeBoundingBox();
            const boundingBox = geometry.boundingBox;
            const center = new THREE.Vector3();
            boundingBox.getCenter(center);
            const size = new THREE.Vector3();
            boundingBox.getSize(size);

            const maxDim = Math.max(size.x, size.y, size.z);
            const scale = 3 / maxDim;

            geometry.translate(-center.x, -center.y, -center.z);
            geometry.scale(scale, scale, scale);

            const material = new THREE.MeshPhongMaterial({ color: 0xcccccc, specular: 0x444444, shininess: 30 });
            const mesh = new THREE.Mesh(geometry, material);

            scene.add(mesh);

            // Animatielus
            const animate = () => {
                requestAnimationFrame(animate);
                mesh.rotation.y += 0.005; // Langzame rotatie
                renderer.render(scene, camera);
            };
            animate();

        }, undefined, function (error) {
            console.error(`Fout bij laden van STL-model ${stlFilename}:`, error);
            container.innerHTML = `<p style="color: #999; text-align: center; padding-top: 50px;">Fout bij laden model.</p>`;
        });
    }
});

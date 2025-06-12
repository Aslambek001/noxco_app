// app/static/js/main.js
// Volledige code main.js - ALLES IN EEN ENKELE DOMContentLoaded BLOK!

// --- IMPORTS VOOR THREE.JS MODULES VERWIJDERD, GEBRUIKEN CDN ---
// ER MOETEN GEEN REGELS ZIJN ZOALS import * as THREE, import { OrbitControls }, import { STLLoader } HIER.

document.addEventListener('DOMContentLoaded', function () {
    // Haal authenticatiestatus en login URL op van globale HTML variabelen (gedefinieerd in base.html)
    const isAuthenticated = typeof IS_AUTHENTICATED !== 'undefined' ? IS_AUTHENTICATED : false;
    const loginUrl = typeof LOGIN_URL !== 'undefined' ? LOGIN_URL : '/login'; // Voorzie een fallback URL

    // Verberg privémodellen en uploadknop voor gasten
    if (!isAuthenticated) {
        document.querySelectorAll('.private-model').forEach(model => {
            model.style.display = 'none';
        });

        const uploadBtn = document.getElementById('openUploadModalBtn');
        if (uploadBtn) {
            uploadBtn.style.display = 'none';
        }
    }

    // --- Functies voor het beheren van het upload modaal venster ---
    const uploadModal = document.getElementById('uploadModal');
    const openUploadModalBtn = document.getElementById('openUploadModalBtn');
    const closeUploadModal = uploadModal?.querySelector('.close-button');
    const cancelUpload = document.getElementById('cancelUpload');
    const stlFile = document.getElementById('stlFile');
    const uploadArea = document.getElementById('uploadArea');
    const uploadPreview = document.getElementById('uploadPreview');
    const fileNameSpan = document.getElementById('fileName');
    const fileSizeSpan = document.getElementById('fileSize');
    const filePreviewImage = document.getElementById('filePreviewImage');

    openUploadModalBtn?.addEventListener('click', function (e) {
        e.preventDefault();
        uploadModal?.classList.add('active');
        document.getElementById('uploadForm')?.reset();
        if (uploadArea) uploadArea.style.display = 'flex';
        if (uploadPreview) uploadPreview.style.display = 'none';
    });

    closeUploadModal?.addEventListener('click', function () {
        uploadModal?.classList.remove('active');
    });

    cancelUpload?.addEventListener('click', function () {
        uploadModal?.classList.remove('active');
        document.getElementById('uploadForm')?.reset();
        if (uploadArea) uploadArea.style.display = 'flex';
        if (uploadPreview) uploadPreview.style.display = 'none';
    });

    uploadModal?.addEventListener('click', function (e) {
        if (e.target === uploadModal) {
            uploadModal.classList.remove('active');
        }
    });

    uploadArea?.addEventListener('click', function () {
        stlFile?.click();
    });

    stlFile?.addEventListener('change', function () {
        if (this.files && this.files.length > 0) {
            const file = this.files[0];
            const allowedExtensions = ['.stl'];
            const fileExtension = file.name.slice((Math.max(0, file.name.lastIndexOf(".")) || Infinity) + 1).toLowerCase();

            if (!allowedExtensions.includes(`.${fileExtension}`)) {
                alert('Ongeldig bestandstype. Selecteer een .stl-bestand.');
                stlFile.value = '';
                if (uploadArea) uploadArea.style.display = 'flex';
                if (uploadPreview) uploadPreview.style.display = 'none';
                return;
            }

            if (fileNameSpan) fileNameSpan.textContent = file.name;
            if (fileSizeSpan) fileSizeSpan.textContent = (file.size / 1024 / 1024).toFixed(2) + ' MB';

            if (uploadArea) uploadArea.style.display = 'none';
            if (uploadPreview) uploadPreview.style.display = 'flex';

            if (filePreviewImage) {
                filePreviewImage.src = 'https://via.placeholder.com/60?text=STL';
                filePreviewImage.alt = 'STL File Preview';
            }
        }
    });

    if (uploadArea) {
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.style.borderColor = '#0095f6';
        }, false);

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.style.borderColor = '#dbdbdb';
        }, false);

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadArea.style.borderColor = '#dbdbdb';
            if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                const file = e.dataTransfer.files[0];
                const allowedExtensions = ['.stl'];
                const fileExtension = file.name.slice((Math.max(0, file.name.lastIndexOf(".")) || Infinity) + 1).toLowerCase();

                if (!allowedExtensions.includes(`.${fileExtension}`)) {
                    alert('Ongeldig bestandstype. Sleep een .stl-bestand hierheen.');
                    return;
                }
                stlFile.files = e.dataTransfer.files;
                const event = new Event('change');
                stlFile.dispatchEvent(event);
            }
        });
    }

    // --- CODE VOOR STL VIEWER HIERONDER ---

    function loadStlModel(containerId, stlFilePath) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('Container for STL viewer not found:', containerId);
            return;
        }

        while (container.firstChild) {
            container.removeChild(container.firstChild);
        }

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xcccccc);
        scene.fog = new THREE.Fog(0xcccccc, 100, 150);

        const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        container.appendChild(renderer.domElement);

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
        scene.add(ambientLight);
        const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.6);
        directionalLight1.position.set(1, 1, 1).normalize();
        scene.add(directionalLight1);
        const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.3);
        directionalLight2.position.set(-1, -1, -1).normalize();
        scene.add(directionalLight2);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.25;
        controls.screenSpacePanning = false;
        controls.minDistance = 1;
        controls.maxDistance = 200;

        const loader = new THREE.STLLoader();
        loader.load(stlFilePath, function (geometry) {
            geometry.computeBoundingBox();
            const boundingBox = geometry.boundingBox;
            const center = new THREE.Vector3();
            boundingBox.getCenter(center);
            const size = new THREE.Vector3();
            boundingBox.getSize(size);

            geometry.translate(-center.x, -center.y, -center.z);

            const material = new THREE.MeshPhongMaterial({ color: 0x0055ff, specular: 0x111111, shininess: 200 });
            const mesh = new THREE.Mesh(geometry, material);
            scene.add(mesh);

            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = camera.fov * (Math.PI / 180);
            let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
            cameraZ *= 2.0;
            camera.position.z = cameraZ;
            camera.position.y = cameraZ / 3;
            camera.position.x = cameraZ / 3;
            camera.lookAt(0,0,0);
            controls.target.set(0,0,0);
            controls.update();

            function animate() {
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }
            animate();

        }, (xhr) => {
            console.log((xhr.loaded / xhr.total * 100).toFixed(0) + '% loaded of ' + stlFilePath);
        }, (error) => {
            console.error('Error loading STL:', error);
            container.innerHTML = '<div style="color: red; text-align: center; padding: 20px;">Fout bij laden model.</div>';
        });

        window.addEventListener('resize', () => {
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        });
    }

    // --- Activering STL-viewers op pagina's (GEGENERALISEERD) ---
    document.querySelectorAll('.stl-viewer-placeholder').forEach(placeholder => {
        const parentItem = placeholder.closest('.profile-gallery-item') || placeholder.closest('.clickable-model-item');
        if (parentItem) {
            const modelFilename = parentItem.dataset.modelFilename;
            const modelId = placeholder.id;
            if (modelFilename && modelId) {
                const stlUrl = `/uploads/stl_models/${modelFilename}`;
                if (placeholder.id !== 'modalStlViewer') { // Laad alleen kleine viewer als het geen modale container is
                    loadStlModel(modelId, stlUrl);
                }
            }
        }
    });

    // --- LOGICA MODAAL VENSTER (GEGENERALISEERD) ---
    const modelModal = document.getElementById('modelModal');
    const closeButtonModalViewer = modelModal?.querySelector('.close-button');

    const clickableGalleryItems = document.querySelectorAll('.profile-gallery-item, .clickable-model-item');

    // --- NIEUWE VARIABELEN VOOR LIKES EN OPMERKINGEN ---
    const likeCountSpan = document.getElementById('likeCount');
    const likeModelBtn = document.getElementById('likeModelBtn');
    const commentsList = document.getElementById('commentsList');
    const newCommentText = document.getElementById('newCommentText');
    const postCommentBtn = document.getElementById('postCommentBtn');
    let currentModelId = null; // Om de ID van het momenteel geopende model op te slaan

    // Functie voor het laden en weergeven van opmerkingen
    async function loadComments(modelId) {
        commentsList.innerHTML = '<div style="text-align: center; color: #888;">Opmerkingen laden...</div>';
        try {
            const response = await fetch(`/api/models/${modelId}/comments`);
            if (!response.ok) {
                throw new Error(`HTTP fout! status: ${response.status}`);
            }
            const data = await response.json(); // Ontvang het hele antwoord
            const comments = data.comments;     // Extract de array uit de 'comments' eigenschap

            commentsList.innerHTML = ''; // Maak oude opmerkingen leeg

            if (comments.length === 0) {
                commentsList.innerHTML = '<div style="text-align: center; color: #888;">Nog geen opmerkingen.</div>';
            } else {
                comments.forEach(comment => {
                    const commentItem = document.createElement('div');
                    commentItem.classList.add('comment-item');
                    commentItem.innerHTML = `
                        <span class="comment-author">${comment.author_username}</span>
                        <span class="comment-text">${comment.text}</span>
                    `;
                    commentsList.appendChild(commentItem);
                });
            }
        } catch (error) {
            console.error('Fout bij het laden van opmerkingen:', error);
            commentsList.innerHTML = '<div style="color: red; text-align: center; padding: 20px;">Fout bij het laden van opmerkingen.</div>';
        }
    }

    // Functie voor het bijwerken van de like-teller
    async function updateLikeCount(modelId) {
        try {
            const response = await fetch(`/api/models/${modelId}/likes`);
            if (!response.ok) {
                throw new Error(`HTTP fout! status: ${response.status}`);
            }
            const data = await response.json();
            if (likeCountSpan) {
                likeCountSpan.textContent = data.likes_count;
            }
        } catch (error) {
            console.error('Fout bij het ophalen van like-aantal:', error);
            if (likeCountSpan) {
                likeCountSpan.textContent = 'N/A';
            }
        }
    }

    clickableGalleryItems.forEach(item => {
        item.addEventListener('click', function(event) {
            if (event.target.closest('a') || event.target.closest('.gallery-item-overlay') || event.target.closest('.post-actions')) {
                return;
            }

            if (!isAuthenticated) {
                window.location.href = loginUrl;
                return;
            }

            const modelId = this.dataset.modelId;
            const modelTitle = this.dataset.modelTitle;
            const modelFilename = this.dataset.modelFilename;
            const modelLocation = this.dataset.modelLocation;
            const modelTags = this.dataset.modelTags;
            const modelDate = this.dataset.modelPosted;
            const authorUsername = this.dataset.authorUsername;
            const authorProfileUrl = this.dataset.authorProfileUrl;

            currentModelId = modelId;

            if (modelModal) {
                document.getElementById('modalModelTitle').textContent = modelTitle;
                document.getElementById('modalModelLocation').textContent = modelLocation || 'N/A';
                document.getElementById('modalModelTags').textContent = modelTags || 'N/A';
                document.getElementById('modalModelDate').textContent = modelDate || 'N/A';

                const authorElement = document.getElementById('modalModelAuthor');
                const authorLinkElement = document.getElementById('modalModelAuthorLink');

                if (authorElement) {
                    authorElement.textContent = authorUsername || 'N/A';
                }
                if (authorLinkElement && authorProfileUrl) {
                    authorLinkElement.href = authorProfileUrl;
                    authorLinkElement.style.display = 'inline';
                } else if (authorLinkElement) {
                    authorLinkElement.style.display = 'none';
                }

                const downloadBtn = document.getElementById('downloadModelBtn');
                if (downloadBtn) {
                    downloadBtn.dataset.modelFilename = modelFilename;
                    downloadBtn.href = `/uploads/stl_models/${modelFilename}`;
                }

                modelModal.classList.add('active');

                if (modelFilename) {
                    loadStlModel('modalStlViewer', `/uploads/stl_models/${modelFilename}`);
                }

                updateLikeCount(modelId);
                loadComments(modelId);
            }
        });
    });

    if (closeButtonModalViewer) {
        closeButtonModalViewer.addEventListener('click', function() {
            if (modelModal) modelModal.classList.remove('active');
        });
    }

    if (modelModal) {
        window.addEventListener('click', function(event) {
            if (event.target == modelModal) {
                modelModal.classList.remove('active');
            }
        });
    }

    // --- Functionaliteit knoppen "like", "opmerking", "download" ---
    document.getElementById('downloadModelBtn')?.addEventListener('click', function(event) {
        console.log("Bestand downloaden: " + this.href);
    });

    // Functie om CSRF-token op te halen (indien gebruikt)
    function getCsrfToken() {
        // Zoek het hidden input veld met de CSRF token.
        // Zorg ervoor dat dit veld bestaat in je base.html of de form die je gebruikt.
        const csrfInput = document.querySelector('input[name="csrf_token"]');
        return csrfInput ? csrfInput.value : '';
    }

    likeModelBtn?.addEventListener('click', async function() {
        if (!currentModelId) {
            console.error('Geen model ID beschikbaar voor liken.');
            return;
        }
        if (!isAuthenticated) {
            window.location.href = loginUrl;
            return;
        }
        try {
            const response = await fetch(`/api/models/${currentModelId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(), // Activeer dit als je CSRF-tokens gebruikt
                },
            });
            if (!response.ok) {
                // Probeer de foutmelding van de server te lezen als deze JSON is
                const errorData = await response.json().catch(() => ({ message: response.statusText }));
                throw new Error(`HTTP fout! status: ${response.status}. Bericht: ${errorData.message || JSON.stringify(errorData)}`);
            }
            const data = await response.json();
            if (likeCountSpan) {
                likeCountSpan.textContent = data.likes_count;
            }
            console.log(`Model ${currentModelId} geliked. Nieuw aantal: ${data.likes_count}. Actie: ${data.action}`);
        } catch (error) {
            console.error('Fout bij het liken van model:', error);
            alert('Fout bij het liken van model. Probeer opnieuw. Details: ' + error.message);
        }
    });

    postCommentBtn?.addEventListener('click', async function() {
        if (!currentModelId) {
            console.error('Geen model ID beschikbaar voor opmerking.');
            return;
        }
        if (!isAuthenticated) {
            window.location.href = loginUrl;
            return;
        }

        const commentText = newCommentText?.value.trim();
        if (!commentText) {
            alert('Opmerking mag niet leeg zijn.');
            return;
        }

        try {
            const response = await fetch(`/api/models/${currentModelId}/comments`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(), // Activeer dit als je CSRF-tokens gebruikt
                },
                body: JSON.stringify({ text: commentText })
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ message: response.statusText }));
                throw new Error(`HTTP fout! status: ${response.status}. Bericht: ${errorData.message || JSON.stringify(errorData)}`);
            }
            const newComment = await response.json();

            if (newCommentText) {
                newCommentText.value = '';
            }

            loadComments(currentModelId);
            console.log('Opmerking geplaatst:', newComment);

        } catch (error) {
            console.error('Fout bij het plaatsen van opmerking:', error);
            alert('Fout bij het plaatsen van opmerking. Probeer opnieuw. Details: ' + error.message);
        }
    });

    document.getElementById('commentModelBtn')?.addEventListener('click', function() {
        commentsList.scrollTop = commentsList.scrollHeight;
        newCommentText?.focus();
    });
});
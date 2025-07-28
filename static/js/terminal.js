class TerminalNav {
    constructor() {
        this.terminal = document.querySelector('.terminal-nav');
        
        // Create terminal content container
        this.terminalContent = document.createElement('div');
        this.terminalContent.className = 'terminal-content';
        
        // Move existing content to the new container
        while (this.terminal.firstChild) {
            this.terminalContent.appendChild(this.terminal.firstChild);
        }
        this.terminal.appendChild(this.terminalContent);
        
        this.input = document.querySelector('.terminal-input');
        this.inputDisplay = document.createElement('div');
        this.inputDisplay.className = 'terminal-input-display';
        this.input.parentNode.appendChild(this.inputDisplay);
        
        this.output = document.querySelector('.terminal-output');
        this.viewToggle = document.querySelector('.modern-view-toggle');
        this.cursor = document.querySelector('.cursor');
        
        // Check if this is a new session
        const lastVisit = sessionStorage.getItem('lastVisit');
        const currentTime = new Date().getTime();
        
        // Detect mobile device
        this.isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        
        // Set initial view based on device and stored preference
        this.initializeView();
        
        // Always start at home directory in new sessions
        if (!lastVisit) {
            localStorage.removeItem('terminalOutput');
            this.currentDir = '~';
            this.clearTerminal();
        } else {
            const savedOutput = localStorage.getItem('terminalOutput');
            this.currentDir = '~';  // Always start at home
            if (savedOutput) {
                this.output.innerHTML = savedOutput;
                requestAnimationFrame(() => {
                    const inputLine = this.input.parentElement;
                    inputLine.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                });
            } else {
                this.printWelcomeMessage();
            }
        }

        // Update session timestamp
        sessionStorage.setItem('lastVisit', currentTime.toString());
        
        // Focus input if in terminal view
        if (!document.body.classList.contains('modern-view')) {
            this.input.focus();
        }

        // Remove previous scroll handler
        this.output.removeEventListener('DOMNodeInserted', this.forceScrollToBottom);
        
        // Add mutation observer to handle new content
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length > 0) {
                    this.checkOverflow();
                    // Only auto-scroll if we have overflow
                    if (this.output.classList.contains('has-overflow')) {
                        const lastNode = mutation.addedNodes[mutation.addedNodes.length - 1];
                        if (lastNode.nodeType === Node.ELEMENT_NODE) {
                            lastNode.scrollIntoView({ behavior: 'smooth', block: 'end' });
                        }
                    }
                }
            });
        });

        // Start observing the output element
        observer.observe(this.output, { childList: true });

        // Get current page from body classes
        const bodyClasses = document.body.classList;
        if (bodyClasses.contains('home-page')) this.currentPage = 'home';
        else if (bodyClasses.contains('about-page')) this.currentPage = 'about';
        else if (bodyClasses.contains('projects-page')) this.currentPage = 'projects';
        else if (bodyClasses.contains('contact-page')) this.currentPage = 'contact';
        else this.currentPage = 'home';
        
        this.content = {
            home: {
                title: "Welcome to Vaishnav Anand's Portfolio",
                description: "I'm a software engineer passionate about AI and machine learning, creating innovative solutions that push boundaries.",
                sections: [
                    "Featured Work",
                    "Recent Achievements",
                    "Latest Updates"
                ]
            },
            about: {
                bio: "As a young developer and researcher, I blend technical expertise with creative problem-solving to build solutions that matter.",
                education: "Stanford University Precollegiate Program",
                skills: [
                    "Python", "JavaScript", "Machine Learning",
                    "Computer Vision", "Web Development"
                ],
                interests: [
                    "Artificial Intelligence",
                    "Robotics",
                    "Financial Technology",
                    "Healthcare AI"
                ]
            },
            projects: {
                'geospatial': {
                    name: 'Geospatial Deepfake Detection',
                    description: 'Advanced GAN-based system achieving 93% accuracy in detecting manipulated satellite imagery.',
                    tech: ['Python', 'TensorFlow', 'GANs', 'Computer Vision'],
                    stats: {
                        accuracy: '93%',
                        'images processed': '50K+',
                        award: '2nd Place'
                    }
                },
                'eyetracking': {
                    name: 'Eye Tracking for Autism Detection',
                    description: 'CNN-based YOLO model achieving 80%+ accuracy in early autism detection through eye movement pattern analysis.',
                    tech: ['Python', 'YOLO', 'OpenCV'],
                    stats: {
                        accuracy: '80%+',
                        'data points': '10K'
                    }
                },
                'stocks': {
                    name: 'Stock Market Analysis',
                    description: 'Statistical correlation study published in the Journal of Student Research, analyzing market patterns and predictive indicators.',
                    tech: ['Python', 'Pandas', 'NumPy'],
                    stats: {
                        'years data': '5+',
                        stocks: '100+'
                    }
                },
                'robotics': {
                    name: 'FTC Robotics Control System',
                    description: 'Advanced autonomous navigation and control system for FTC robotics competition, leading to Connect Award victory.',
                    tech: ['Java', 'Android SDK', 'OpenCV'],
                    stats: {
                        place: '1st',
                        accuracy: '95%'
                    }
                }
            },
            contact: {
                email: "vaishnavanand90@gmail.com",
                github: "github.com/yourusername",
                linkedin: "linkedin.com/in/yourusername",
                message: "I'm always open to discussing new projects and opportunities."
            }
        };

        this.commands = {
            'help': () => this.showHelp(),
            'clear': () => this.clearTerminal(),
            'ls': () => this.listContent(),
            'pwd': () => this.showCurrentDir(),
            'cd': (args) => this.changeDirectory(args),
            'cat': (args) => this.showContent(args),
            'modern': () => this.toggleView(),
            'switch': () => this.toggleView(),
            'home': () => this.navigateTo('home'),
            'about': () => this.navigateTo('about'),
            'projects': () => this.navigateTo('projects'),
            'contact': () => this.navigateTo('contact'),
            'view': (args) => this.viewProject(args),
            'hathor': () => this.openExternalSite('https://hathor.it.com/', 'Hathor - Sustainable Fashion Marketplace'),
            'navtype': () => this.openExternalSite('https://navtype.com/', 'NavType - Typing Speed Test'),
            'theme': (args) => this.handleTheme(args)
        };
        
        this.setupEventListeners();

        // Add mobile-specific event handlers
        this.setupMobileHandlers();

        // Initialize theme
        this.initializeTheme();
    }

    setupEventListeners() {
        this.viewToggle.addEventListener('click', () => this.toggleView());
        
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.handleCommand(this.input.value.trim());
                this.input.value = '';
                this.updateInputDisplay();
            }
        });

        // Handle cursor movement and input display
        this.input.addEventListener('input', () => {
            this.updateInputDisplay();
            // Ensure input is visible when typing
            const inputLine = this.input.parentElement;
            inputLine.scrollIntoView({ behavior: 'smooth', block: 'end' });
            this.terminal.scrollBy(0, 40);
        });

        this.input.addEventListener('keyup', () => {
            this.updateInputDisplay();
        });

        this.input.addEventListener('click', () => {
            this.updateInputDisplay();
        });

        // Handle click on terminal to focus input
        this.terminal.addEventListener('click', () => {
            this.input.focus();
        });

        // Update cursor position on selection change
        this.input.addEventListener('select', () => {
            this.updateInputDisplay();
        });

        // Add contact form submission handler
        const contactForm = document.querySelector('#contact-form');
        if (contactForm) {
            contactForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleContactSubmit(e.target);
            });
        }
    }

    setupMobileHandlers() {
        // Detect if we're on a mobile device
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        
        if (isMobile) {
            // Handle keyboard showing/hiding on iOS
            if (window.visualViewport) {
                window.visualViewport.addEventListener('resize', () => {
                    if (document.activeElement === this.input) {
                        requestAnimationFrame(() => {
                            const inputLine = this.input.parentElement;
                            inputLine.scrollIntoView({ behavior: 'smooth', block: 'end' });
                            // Additional scroll to ensure the input is visible above the keyboard
                            setTimeout(() => {
                                this.terminal.scrollBy(0, window.visualViewport.height * 0.3);
                            }, 100);
                        });
                    }
                });
            }

            // Improve touch handling
            this.terminal.addEventListener('touchstart', () => {
                if (document.activeElement !== this.input) {
                    this.input.focus();
                }
            });
        }
    }

    updateInputDisplay() {
        const text = this.input.value;
        const cursorPos = this.input.selectionStart;
        this.inputDisplay.textContent = text;
        
        // Calculate cursor position based on text width
        const promptWidth = this.getTextWidth('$ '); // Get width of prompt
        
        if (cursorPos === 0) {
            // Position cursor right after the prompt
            this.cursor.style.left = `calc(8px + ${promptWidth}px)`;
        } else {
            const textBeforeCursor = text.substring(0, cursorPos);
            const textWidth = this.getTextWidth(textBeforeCursor);
            this.cursor.style.left = `calc(8px + ${promptWidth}px + ${textWidth}px)`;
        }
    }

    getTextWidth(text) {
        // Create a temporary span to measure text width
        const span = document.createElement('span');
        span.style.visibility = 'hidden';
        span.style.position = 'absolute';
        span.style.whiteSpace = 'pre';
        span.style.font = getComputedStyle(this.input).font;
        span.textContent = text;
        document.body.appendChild(span);
        const width = span.offsetWidth;
        document.body.removeChild(span);
        return width;
    }

    toggleView() {
        document.body.classList.toggle('modern-view');
        // Store view preference only when explicitly toggled
        localStorage.setItem('viewPreference', 
            document.body.classList.contains('modern-view') ? 'modern' : 'terminal'
        );
        this.updateViewToggleButton();
        
        if (!document.body.classList.contains('modern-view')) {
            this.input.focus();
        }
    }

    updateViewToggleButton() {
        const isModernView = document.body.classList.contains('modern-view');
        this.viewToggle.innerHTML = isModernView 
            ? '<i class="fas fa-terminal"></i> Switch to Terminal View'
            : '<i class="fas fa-window-maximize"></i> Switch to Modern View';
    }

    navigateTo(page) {
        // Store current terminal state and directory in localStorage before navigation
        localStorage.setItem('terminalOutput', this.output.innerHTML);
        localStorage.setItem('terminalCurrentDir', this.currentDir);
        const routes = {
            'home': '/',
            'about': '/about',
            'projects': '/projects',
            'contact': '/contact'
        };
        window.location.href = routes[page];
    }

    showContent(args) {
        if (!args.length) {
            this.print('Please specify what to show. Example: cat about');
            return;
        }

        const section = args[0].toLowerCase();
        if (section === 'home') {
            this.showHome();
        } else if (section === 'about') {
            this.showAbout();
        } else if (section === 'contact') {
            this.showContact();
        } else if (section === 'projects') {
            this.showProjects();
        } else if (this.content.projects[section]) {
            this.viewProject([section]);
        } else {
            this.print(`Content not found: ${section}`);
        }
        // Force scroll to bottom after showing content
        this.forceScrollToBottom();
    }

    showHome() {
        const home = this.content.home;
        const homeText = `
${home.title}
${'-'.repeat(home.title.length)}
${home.description}

Sections:
${home.sections.map(s => '- ' + s).join('\n')}
`;
        this.print(homeText);
    }

    showAbout() {
        const about = this.content.about;
        const aboutText = `
About Me:
${about.bio}

Education:
${about.education}

Skills:
${about.skills.join(', ')}

Interests:
${about.interests.map(i => '- ' + i).join('\n')}
`;
        this.print(aboutText);
    }

    showContact() {
        const contact = this.content.contact;
        const contactText = `
Contact Information:
${'-'.repeat(20)}
Email: ${contact.email}
GitHub: ${contact.github}
LinkedIn: ${contact.linkedin}

${contact.message}
`;
        this.print(contactText);
    }

    showProjects() {
        const projects = this.content.projects;
        const projectsList = Object.entries(projects).map(([key, project]) => {
            return `${key}: ${project.name}`;
        }).join('\n');

        const projectsText = `
Available Projects:
${'-'.repeat(17)}
${projectsList}

Use 'view <project>' to see details (e.g., 'view geospatial')
`;
        this.print(projectsText);
    }

    changeDirectory(args) {
        if (!args.length) {
            this.print('Please specify a directory');
            return;
        }

        const dir = args[0];
        if (dir === '..') {
            this.currentDir = '~';
            this.print('Changed to: ' + this.currentDir);
        } else if (['home', 'about', 'projects', 'contact'].includes(dir)) {
            this.currentDir = '~/' + dir;
            this.print('Changed to: ' + this.currentDir);
            this.showContent([dir]);
        } else {
            this.print('Directory not found: ' + dir);
        }
        // Store current directory in localStorage
        localStorage.setItem('terminalCurrentDir', this.currentDir);
    }

    listContent() {
        if (this.currentDir === '~') {
            this.print(`
Available directories:
  home/     - Home page
  about/    - About me and skills
  projects/ - Portfolio projects
  contact/  - Contact information
            `);
        } else {
            const section = this.currentDir.split('/')[1];
            this.showContent([section]);
        }
    }

    showHelp() {
        const helpText = `
Available commands:
  help                 Show this help message
  ls                   List contents of current directory
  cd <dir>            Change directory (home, about, projects, contact, ..)
  cat <section>       Show content of a section
  view <project>      View details of a specific project
  clear               Clear the terminal
  pwd                 Print working directory
  modern              Switch to modern view
  switch              Switch to modern view (alias)
  theme [light|dark]  Switch terminal theme
  home                Go to home page
  about               Go to about page
  projects            Go to projects page
  contact             Go to contact page
  hathor              Open Hathor - Sustainable Fashion Marketplace
  navtype             Open NavType - Typing Speed Test
  
Example: cd projects
Example: view geospatial
Example: cat about
Example: theme light
`;
        this.print(helpText);
    }

    printWelcomeMessage() {
        const message = `Welcome to Vaishnav Anand's Portfolio Terminal v1.0.0
=================================================
This is an interactive terminal interface to explore my portfolio.
You can navigate through my work, skills, and experience using terminal commands.

Type 'help' to see available commands
Type 'modern' to switch to modern view
current directory: ${this.currentDir}
type a command to begin...

`;
        this.print(message);
    }

    print(text, isError = false) {
        const line = document.createElement('div');
        line.textContent = text;
        if (isError) {
            line.style.color = '#ff6b6b';
        }
        this.output.appendChild(line);
        
        // Improved scrolling for mobile
        requestAnimationFrame(() => {
            line.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            if (/iPhone|iPad|iPod/i.test(navigator.userAgent)) {
                // Extra scroll for iOS to ensure content is visible above keyboard
                setTimeout(() => {
                    this.terminal.scrollBy(0, 100);
                }, 100);
            }
        });
    }

    forceScrollToBottom() {
        requestAnimationFrame(() => {
            const inputLine = this.input.parentElement;
            inputLine.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        });
    }

    handleCommand(input) {
        const [cmd, ...args] = input.toLowerCase().split(' ');
        this.print(`${this.currentDir} $ ${input}`);
        
        if (this.commands[cmd]) {
            this.commands[cmd](args);
            // Ensure proper scrolling after command execution
            requestAnimationFrame(() => {
                const inputLine = this.input.parentElement;
                inputLine.scrollIntoView({ behavior: 'smooth', block: 'end' });
                if (/iPhone|iPad|iPod/i.test(navigator.userAgent)) {
                    setTimeout(() => {
                        this.terminal.scrollBy(0, 100);
                    }, 100);
                }
            });
        } else {
            this.print(`Command not found: ${cmd}. Type 'help' for available commands.`, true);
        }
    }

    clearTerminal() {
        this.output.innerHTML = '';
        this.currentDir = '~';
        localStorage.removeItem('terminalCurrentDir');
        this.printWelcomeMessage();
        // Clear stored terminal history
        localStorage.removeItem('terminalOutput');
        // Ensure we're scrolled to top
        this.terminal.scrollTop = 0;
    }

    showCurrentDir() {
        this.print(this.currentDir);
    }

    viewProject(args) {
        if (!args.length) {
            this.print('Please specify a project name. Example: view geospatial', true);
            return;
        }

        const projectKey = args[0].toLowerCase();
        const project = this.content.projects[projectKey];

        if (!project) {
            this.print(`Project '${projectKey}' not found. Type 'ls' to see available projects.`, true);
            return;
    }

        const projectInfo = `
Project: ${project.name}
${'-'.repeat(project.name.length + 9)}
Description: ${project.description}

Technologies: ${project.tech.join(', ')}

Statistics:
${Object.entries(project.stats)
    .map(([key, value]) => `  ${key}: ${value}`)
    .join('\n')}
`;
        this.print(projectInfo);
    }

    openExternalSite(url, description) {
        this.print(`Opening ${description}...`);
        window.open(url, '_blank');
    }

    initializeView() {
        const storedPreference = localStorage.getItem('viewPreference');
        
        // Default to modern view on mobile devices if no preference is stored
        if (this.isMobile && !storedPreference) {
            document.body.classList.add('modern-view');
            localStorage.setItem('viewPreference', 'modern');
        } else if (storedPreference === 'modern') {
            document.body.classList.add('modern-view');
        } else if (storedPreference === 'terminal') {
            document.body.classList.remove('modern-view');
        }
        
        this.updateViewToggleButton();
        
        // Handle orientation changes on mobile
        if (this.isMobile) {
            window.addEventListener('orientationchange', () => {
                setTimeout(() => {
                    this.adjustMobileLayout();
                }, 100);
            });
            
            // Initial layout adjustment
            this.adjustMobileLayout();
        }
    }
    
    adjustMobileLayout() {
        if (document.body.classList.contains('modern-view')) {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        }
    }

    initializeTheme() {
        const storedTheme = localStorage.getItem('terminalTheme');
        if (storedTheme === 'light') {
            document.body.classList.add('light-theme');
        }
    }

    handleTheme(args) {
        if (!args.length) {
            const currentTheme = document.body.classList.contains('light-theme') ? 'light' : 'dark';
            this.print(`Current theme: ${currentTheme}\nUsage: theme [light|dark]`);
            return;
        }

        const theme = args[0].toLowerCase();
        if (theme !== 'light' && theme !== 'dark') {
            this.print('Invalid theme. Use: theme [light|dark]', true);
            return;
        }

        const body = document.body;
        if (theme === 'light') {
            body.classList.add('light-theme');
        } else {
            body.classList.remove('light-theme');
        }

        localStorage.setItem('terminalTheme', theme);
        this.print(`Theme switched to ${theme} mode`);
    }
}

// Initialize the terminal when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TerminalNav();
}); 
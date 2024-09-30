const text = this.getAttribute('data-clipboard-text');
navigator.clipboard.writeText(text);
this.setAttribute('disabled', true);
const label = this.innerText;
this.innerText = 'Copied!';
setTimeout(() => {
    this.innerText = label;
    this.removeAttribute('disabled');
}, 1000);
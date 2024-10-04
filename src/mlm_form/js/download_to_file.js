const blob = new Blob([this.getAttribute('data-file-content')], { type: 'application/json' });
const a = document.createElement('a');
a.download = this.getAttribute('data-file-name');
a.href = window.URL.createObjectURL(blob);
a.dataset.downloadurl = ['application/json', a.download, a.href].join(':');
a.style.display = "none";
document.body.appendChild(a);
a.click();
document.body.removeChild(a);
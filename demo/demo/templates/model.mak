<h1>Entries in the HelloWorld model</h1>

<ul>
  % for entry in entries[::-1]:
      <li>${str(entry.id)} - ${entry.message} - ${str(entry.timestamp)}</li>
  % endfor
</ul>

<?php
// KeenTool Mail Layout v1.0.1 — 2026-10-26, stable release.
// Shared email-only renderer: escaped text, metric/report tables and lossless diagnostic fallback.
function kmailEscape($text) { return htmlspecialchars((string)$text,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8'); }
function kmailTitle($text) { return preg_replace('/^[^\p{L}\p{N}]+/u','',trim($text))??trim($text); }
function kmailCount($text) { return preg_match('/^[0-9]+$/D',(string)$text)?preg_replace('/\B(?=(\d{3})+(?!\d))/','.',(string)$text):(string)$text; }
function kmailTable($headings,$rows) {
    $html='<table width="100%" cellpadding="0" cellspacing="0" style="width:100%;border-collapse:collapse;table-layout:fixed;font-size:13px;line-height:1.5">';
    if($headings){$html.='<thead><tr>';foreach($headings as $index=>$heading){$width=($headings[0]??'')==='Hop'?' width="'.[10,30,18,42][$index].'%"':'';$html.='<th scope="col" align="left"'.$width.' style="padding:10px 8px;border-bottom:2px solid #dbe3e9;background:#f3f6f8;color:#52606d;font-weight:600">'.kmailEscape($heading).'</th>';}$html.='</tr></thead>';}
    $html.='<tbody>';foreach($rows as $row){$html.="\r\n<tr>";foreach($row as $cell)$html.='<td valign="top" style="padding:10px 8px;border-bottom:1px solid #e7edf1;overflow-wrap:anywhere;word-break:break-word">'.$cell.'</td>';$html.='</tr>';}
    return $html.'</tbody></table>';
}
function kmailPre($text) {
    return '<pre style="margin:12px 0;padding:12px;background:#17202b;color:#d6e3ed;font:12px/1.6 Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word">'.kmailEscape($text).'</pre>';
}
function kmailMtr($report) {
    // Never assign diagnostic columns by position unless the standard header is present.
    if(!preg_match('/^HOST:\s*.*?\s+Loss%\s+Snt\s+Last\s+Avg\s+Best\s+Wrst\s+StDev\s*$/m',$report))return kmailPre($report);
    $rows=[];$extra=[];$meta=[];
    foreach(explode("\n",$report) as $line){
        if(preg_match('/^\s*(\d+)\.\|[-+`]*\s*(.+?)\s+([0-9]+(?:\.[0-9]+)?)%?\s+(\d+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s*$/D',$line,$m)){
            $rows[]=[kmailEscape($m[1]),'<span style="font-family:Consolas,monospace">'.kmailEscape($m[2]).'</span>','Loss <strong>'.kmailEscape($m[3].'%').'</strong><br>Sent '.kmailEscape($m[4]),'Avg <strong>'.kmailEscape($m[6]).'</strong> · Last '.kmailEscape($m[5]).'<br>Best '.kmailEscape($m[7]).' · Worst '.kmailEscape($m[8]).'<br>StDev '.kmailEscape($m[9])];
        }elseif(preg_match('/^Start:\s*(.*)$/',$line,$m))$meta[]='Started: '.$m[1];
        elseif(preg_match('/^HOST:\s*(.*?)\s+Loss%\s+Snt\s+Last\s+Avg\s+Best\s+Wrst\s+StDev\s*$/',$line,$m))$meta[]='Host: '.$m[1];
        elseif(trim($line)!=='')$extra[]=$line;
    }
    if(!$rows)return kmailPre($report);
    $html='';foreach($meta as $text)$html.='<p style="margin:6px 0;color:#52606d;font-size:12px">'.kmailEscape($text).'</p>';
    $html.=kmailTable(['Hop','Host','Probes','Latency (ms)'],$rows);
    $html.='<p style="margin:12px 0;color:#52606d;font-size:12px">Intermediate-hop loss can reflect ICMP rate limiting. Compare the final hop; this trace was collected after the ping check.</p>';
    if($extra)$html.=kmailPre(implode("\n",$extra));
    return $html;
}
function kmailValue($label,$value) {
    $color='#17202b';$key=strtolower($label);
    if($key==='firewall healthy')$color=$value==='yes'?'#00843d':($value==='no'?'#bd3030':'#966000');
    elseif($key==='web privileges')$color=$value==='unprivileged detected'?'#00843d':($value==='root detected'?'#bd3030':'#966000');
    elseif($key==='packet loss'&&preg_match('/^([0-9.]+)%/',$value,$m))$color=(float)$m[1]>=100?'#bd3030':((float)$m[1]>0?'#966000':'#00843d');
    elseif($key==='latency'&&preg_match('/^([0-9.]+) ms \(Threshold: ([0-9.]+) ms\)/',$value,$m))$color=(float)$m[1]>(float)$m[2]?'#966000':'#00843d';
    if(in_array($key,['total threats blocked','blacklist size','autoban (trap)','geoip blocks'],true)&&preg_match('/^([0-9]+)(.*)$/D',$value,$m))$value=kmailCount($m[1]).$m[2];
    return '<span style="font-weight:600;color:'.$color.'">'.kmailEscape($value).'</span>';
}
function kmailContent($text) {
    $lines=explode("\n",str_replace(["\r\n","\r"],"\n",$text));$html='';$i=0;$length=count($lines);
    while($i<$length){
        $line=trim($lines[$i]);if($line===''){$i++;continue;}
        if(preg_match('/^---.*MTR.*---$/i',$line)||preg_match('/^(?:Start:|HOST:)/',$line)){
            if(str_starts_with($line,'---'))$i++;
            $html.='<h3 style="font-size:16px;margin:24px 0 12px;color:#17202b">MTR diagnostic report</h3>'.kmailMtr(implode("\n",array_slice($lines,$i)));break;
        }
        // opkg update listings: preserve package names and complete installed/available versions.
        if(preg_match('/^([a-zA-Z0-9+_.-]+) - (.+?) - (.+)$/D',$line)){
            $rows=[];while($i<$length&&preg_match('/^([a-zA-Z0-9+_.-]+) - (.+?) - (.+)$/D',trim($lines[$i]),$m)){$rows[]=[kmailEscape($m[1]),kmailEscape($m[2]),kmailEscape($m[3])];$i++;}
            $html.=kmailTable(['Package','Installed','Available'],$rows);continue;
        }
        $clean=kmailTitle($line);
        if(preg_match('/^(Top Attackers|Top Targeted Ports):$/i',$clean,$m)){
            $ports=strcasecmp($m[1],'Top Targeted Ports')===0;$rows=[];$i++;
            while($i<$length&&preg_match('/^\s*-\s+(.+):\s+([0-9]+) hits\s*$/D',$lines[$i],$entry)){
                $name=$ports?preg_replace('/^Port\s+/','',$entry[1]):$entry[1];$rows[]=[kmailEscape($name),'<strong>'.kmailEscape(kmailCount($entry[2])).'</strong>'];$i++;
            }
            $html.='<h3 style="font-size:16px;margin:24px 0 12px;color:#17202b">'.kmailEscape($m[1]).'</h3>';
            if($rows)$html.=kmailTable([$ports?'Port':'IP address','Hits'],$rows);
            continue;
        }
        if(preg_match('/^[A-Za-z][A-Za-z0-9 \/()_.%-]{0,70}:$/D',$clean)){
            $html.='<h3 style="font-size:16px;margin:24px 0 12px;color:#17202b">'.kmailEscape(rtrim($clean,':')).'</h3>';$i++;continue;
        }
        $rows=[];
        while($i<$length){
            $current=trim($lines[$i]);$labelLine=kmailTitle($current);
            if(!preg_match('/^([A-Za-z][A-Za-z0-9 \/()_.%-]{0,70}):\s+(.+)$/D',$labelLine,$m)||in_array($m[1],['Start','HOST','Recent events'],true))break;
            $rows[]=[kmailEscape($m[1]),kmailValue($m[1],$m[2])];$i++;
        }
        if($rows){$html.=kmailTable([],$rows);continue;}
        // Every unrecognized line is retained verbatim as escaped text.
        $html.='<p style="margin:12px 0;line-height:1.65;overflow-wrap:anywhere">'.kmailEscape($line).'</p>';$i++;
    }
    return $html;
}
function kmailLayout($subject,$text,$custom='') {
    $category='Router notification';$status='Information';$color='#0097dc';
    if(str_starts_with($subject,'Ping Alert:')){$category='Connection Monitor';$status='Warning';$color='#966000';if(preg_match('/Packet Loss:\s*100(?:\.0+)?%/',$text)){$status='Target unreachable';$color='#bd3030';}}
    elseif(str_starts_with($subject,'Ping target reachable again:')){$category='Connection Monitor';$status='Target reachable';$color='#00843d';}
    elseif(str_starts_with($subject,'WAN ')){$category='WAN / PPP';$status=str_contains($subject,' recovered ')?'PPP restored':'PPP disconnected';$color=str_contains($subject,' recovered ')?'#00843d':'#bd3030';}
    elseif(str_starts_with($subject,'Entware:')){$category='Entware';$status='Updates';if(str_contains($subject,'upgrade result')){$status=str_starts_with($text,'completed')?'Upgrade completed':'Review required';$color=$status==='Upgrade completed'?'#00843d':'#bd3030';}}
    elseif(preg_match('/^Firewall .* Summary$/',$subject)){$category='Firewall';$status='Activity report';}
    elseif(str_contains(strtolower($subject),'security summary')){$category='Security & Health';$status='Daily summary';}
    elseif(str_contains(strtolower($subject),'health warning')){$category='Security & Health';$status='Warning';$color='#966000';}
    elseif(str_contains(strtolower($subject),'blocklist update failed')){$category='Firewall';$status='Update failed';$color='#bd3030';}
    $title=preg_replace('/^KeenTool:\s*/','',$subject);$title=ucfirst($title);
    if($custom!==''){
        $content=preg_match('/<body\b[^>]*>(.*?)<\/body>/is',$custom,$match)?$match[1]:$custom;
        $content=preg_replace('/^\s*<h2\b[^>]*>KeenTool security summary<\/h2>\s*/i','',$content);
    }else $content=kmailContent($text);
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'.kmailEscape($title).'</title></head>' ."\r\n".
      '<body style="margin:0;padding:0;background:#edf0f4;color:#17202b;font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.6"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="width:100%;background:#edf0f4"><tr><td align="center" style="padding:24px 10px">' ."\r\n".
      '<table role="presentation" width="720" cellpadding="0" cellspacing="0" style="width:100%;max-width:720px;background:#ffffff;border:1px solid #dbe3e9;border-radius:8px"><tr><td style="padding:22px 24px;border-bottom:1px solid #e7edf1"><span style="font-size:22px;font-weight:700;letter-spacing:2px;color:#0097dc">KEENTOOL</span><br><span style="font-size:12px;color:#52606d">'.kmailEscape($category).'</span></td></tr>' ."\r\n".
      '<tr><td style="padding:24px 24px 8px"><span style="font-size:12px;font-weight:700;color:'.$color.'">'.kmailEscape($status).'</span><h1 style="margin:10px 0 12px;font-size:23px;line-height:1.35;font-weight:600;color:#17202b;overflow-wrap:anywhere">'.kmailEscape($title).'</h1></td></tr>' ."\r\n".
      '<tr><td style="padding:0 24px 24px">'.$content.'</td></tr>' ."\r\n".
      '<tr><td style="padding:16px 24px;border-top:1px solid #e7edf1;color:#52606d;font-size:11px;line-height:1.6">Automated notification from KeenTool<br>&copy; '.date('Y').' mattheweli</td></tr></table></td></tr></table></body></html>';
}
if(PHP_SAPI==='cli'&&realpath($_SERVER['SCRIPT_FILENAME']??'')===__FILE__){
    $parts=explode("\0",stream_get_contents(STDIN),3);if(count($parts)!==3){fwrite(STDERR,"Invalid mail layout input\n");exit(1);}
    $html=kmailLayout($parts[0],$parts[1],$parts[2]);echo in_array('--quoted-printable',$argv,true)?quoted_printable_encode($html):$html;
}

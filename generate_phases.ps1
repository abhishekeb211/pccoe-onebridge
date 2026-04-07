$content = Get-Content -Path "project_phases.md" -Raw

# Regex to find each phase block
$pattern = '###\s+(Phase (\d+):[^\n]+)\n- \*\*Function Summary:\*\*\s+([^\n]+)\n- \*\*Module Working:\*\*\s+([^\n]+)\n- \*\*Task:\*\*\s+([^\n]+)'
$matches = [regex]::Matches($content, $pattern)

foreach ($match in $matches) {
    $fullTitle = $match.Groups[1].Value
    $phaseNum = $match.Groups[2].Value
    $functionSummary = $match.Groups[3].Value
    $moduleWorking = $match.Groups[4].Value
    $taskText = $match.Groups[5].Value

    # Clean up title for filename
    $safeTitle = $fullTitle -replace '[^\w\s-]', ''
    $safeTitle = $safeTitle -replace '\s+', '_'
    $fileName = "phase_docs\$safeTitle.md"

    # Infer libraries based on keywords
    $lowerTitle = $fullTitle.ToLower()
    $libs = "- HTML5, CSS3, Vanilla JS`n- Standard DOM API"
    if ($lowerTitle -match "backend" -or $lowerTitle -match "api" -or $lowerTitle -match "gateway" -or $lowerTitle -match "database") {
        $libs = "- Python (FastAPI)`n- SQLite/PostgreSQL`n- Pydantic`n- HTTPX (for external API calls)"
    }
    if ($lowerTitle -match "ai" -or $lowerTitle -match "agent" -or $lowerTitle -match "nlp" -or $lowerTitle -match "gemini") {
        $libs = "- OpenRouter API SDK`n- Google Generative AI bindings`n- HuggingFace Transformers (Local agent)`n- Pandas (Data curation)"
    }
    if ($lowerTitle -match "auth" -or $lowerTitle -match "security" -or $lowerTitle -match "rbac") {
        $libs = "- JWT (JSON Web Tokens)`n- bcrypt/Argon2`n- OAuth2 Middleware"
    }

    # Generate Detailed Content
    $fileContent = @"
# $fullTitle

## 1. Module Overview
**Functionality**: $functionSummary
**Working Mechanism**: $moduleWorking

## 2. Detailed Tasks
- [ ] Review system requirements against PRD for this phase.
- [ ] Establish initial sandbox/development branch for $phaseNum.
- [ ] Execute Core Task: $taskText
- [ ] Perform unit testing on the specific modules integrated.
- [ ] Conduct accessibility and security review before requesting a merge.

## 3. Requirements
**Functional Requirements:**
- Must successfully fulfill the working mechanism: $moduleWorking.
- Output must be integrated securely and without latency impacting the main thread.

**Non-Functional Requirements:**
- **Performance:** Sub-200ms response time for local functions, optimized async calls for external ones.
- **Privacy:** Anonymize all data if interfacing with external LLMs.
- **Accessibility:** Ensure all new UI complies with WCAG 2.1 AA standards.

## 4. Libraries & Tech Stack
$libs
- Git & GitHub CLI (Version Control)

"@

    Set-Content -Path $fileName -Value $fileContent
    Write-Host "Generated $fileName"
}

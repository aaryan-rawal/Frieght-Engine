# Provider integration readiness

All provider credentials remain in the owner's local secret configuration. This report does not inspect `.env`, contact providers, send SMS, or submit identity/regulatory data.

| Integration | Local code | Safe local behavior | Still required |
|---|---|---|---|
| SMS / registration OTP | Twilio and generic HTTPS adapter exist. Provider configuration requires credentials and sender details. | When no provider is configured, non-production may show a development OTP; production returns 503. Development logs no longer contain the OTP or phone number. No SMS was sent during this work. | Provider account, verified sender/number, consent, template/policy review and owner-supplied credentials before a real send. |
| Identity verification | HTTPS provider adapter and configuration status exist. | With no configured provider, the fleet screen collects no identifiers or documents and can mark the driver `manual_review_required`. Provider submissions require an explicit subject-consent confirmation. Manual review is not a verification pass. | Authorized provider contract, consent/retention/legal review, secure production storage and test credentials before provider-backed testing. |
| E-Way Bill | Provider-neutral HTTPS adapter and normalized response checks exist. | No configured provider returns an unavailable response; no credential or live request was used. | Authorized GSP/provider onboarding and sandbox credentials, approved request/response contract and owner/legal review. |
| Regulatory sources | Eight required checks and source-referenced assessment validation exist. | Missing or untrusted evidence remains `unknown`; no check was marked pass. | Current legal review, provider/authority access, approved trust source and versioned policy evidence. See [the source register](REGULATORY_SOURCE_REGISTER.md). |

The identity checkbox records the company's assertion that the driver consented; it is not legal proof of consent. The organization remains responsible for obtaining and retaining appropriate consent under its approved policy.

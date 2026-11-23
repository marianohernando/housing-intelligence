import type { Metadata } from "next";
import type { ReactNode } from "react";

import CodeBlock from "@/components/developers/CodeBlock";
import styles from "@/components/developers/Developers.module.css";
import CmCount from "@/components/provenance/CmCount";
import SiteFooter from "@/components/shell/SiteFooter";
import GlassCard from "@/components/ui/GlassCard";
import {
  API_BASE,
  API_GROUPS,
  type ApiExample,
  curlOf,
  DEV_TEXT as TEXT,
  ENVELOPE_EXAMPLE,
  MCP_CLAUDE_CODE,
  MCP_CLAUDE_DESKTOP,
  MCP_SETUP,
  MCP_TOOLS,
  PLANNED,
  REPO_URL,
  repoFile,
  repoFolder,
  SECTIONS,
} from "@/lib/developers";

export const metadata: Metadata = {
  title: TEXT.title,
  description:
    "La API pública de Vida Fácil y su servidor MCP: gratis, sin clave y de solo lectura, con los datos abiertos de la Comunidad de Madrid.",
};

const TITLES = Object.fromEntries(SECTIONS.map((s) => [s.id, s.title]));

/** «Para desarrolladores» (D-249): copy from pitch/textos_web.md, section 12. */
function Section({ id, children, badge }: { id: string; children: ReactNode; badge?: string }) {
  return (
    <GlassCard as="section" aria-labelledby={id} className={styles.card}>
      <h2 id={id} className={styles.sectionTitle}>
        {TITLES[id]}
        {badge && <span className={styles.badge}>{badge}</span>}
      </h2>
      {children}
    </GlassCard>
  );
}

function Example({ example }: { example: ApiExample }) {
  return (
    <article className={styles.route} aria-labelledby={`ruta-${example.id}`}>
      <h4 id={`ruta-${example.id}`} className={styles.routeTitle}>
        {example.title}
      </h4>
      <p className={styles.routePath}>
        <span className={styles.method}>{example.method}</span> <code>{example.path}</code>
      </p>
      <p>{example.description}</p>
      <CodeBlock code={curlOf(example)} caption="curl" label={`${example.method} ${example.path}`} />
      <p className={styles.returns}>
        <strong>Qué devuelve:</strong> {example.returns}
      </p>
    </article>
  );
}

export default function DesarrolladoresPage() {
  return (
    <div className={styles.page}>
      <div className={styles.content} data-developers>
        <header className={styles.header}>
          <p className={styles.tag}>{TEXT.tag}</p>
          <h1 className={styles.title}>{TEXT.title}</h1>
          <p className={styles.lead}>{TEXT.intro}</p>
          <nav aria-label={TEXT.tocLabel}>
            <ul className={styles.toc}>
              {SECTIONS.map((s) => (
                <li key={s.id}>
                  <a href={`#${s.id}`}>{s.title}</a>
                </li>
              ))}
            </ul>
          </nav>
        </header>

        <Section id="que-es">
          <p>
            Una API pública y abierta, de solo lectura. <strong>No pide clave ni registro:</strong> haces la petición y
            recibes JSON. Está en el mismo dominio que la web: <code>{API_BASE}</code>.
          </p>
          <p>Cada ruta, con sus campos y sus tipos, está descrita en formato OpenAPI:</p>
          <p>
            <a href={`${API_BASE}/openapi.json`}>{`${API_BASE}/openapi.json`}</a>
          </p>
          <h3 className={styles.subhead}>Todas las respuestas tienen la misma forma</h3>
          <CodeBlock code={ENVELOPE_EXAMPLE} caption="JSON" label="Respuesta: data, meta y warnings" />
          <ul className={styles.list}>
            <li>
              <code>data</code>: la respuesta.
            </li>
            <li>
              <code>meta.methodology_version</code>: la versión del método que calcula las cifras, por ejemplo{" "}
              <code>fit-0.9</code> para el encaje, <code>gap-0.4</code> para «Qué falta» o <code>viability-0.2</code> para la
              viabilidad. Si cambia el método, cambia la versión.
            </li>
            <li>
              <code>meta.data_version</code>: de cuándo son los datos.
            </li>
            <li>
              <code>warnings</code>: avisos que son parte de la respuesta, por ejemplo una fila que aún no está calculada
              para esa zona. Léelos.
            </li>
          </ul>
          <h3 className={styles.subhead}>Sin dato no es 0</h3>
          <p>
            Si no sabemos una cifra, llega como <code>null</code> con su motivo en <code>null_reason</code>, o con el estado{" "}
            <code>SIN_DATOS</code> o <code>UNKNOWN</code>. Nunca la rellenamos con un 0: un 0 es un dato real, por ejemplo
            ninguna parcela pública en una zona. Muchas cifras traen <code>confidence</code>, de 0 a 1: cuánto nos fiamos
            de ellas.
          </p>
          <h3 className={styles.subhead}>Errores</h3>
          <p>
            Una entrada que no vale responde <strong>422</strong> y dice qué campo falla; una zona que no existe,{" "}
            <strong>404</strong>. El detalle va en <code>detail</code>.
          </p>
        </Section>

        <Section id="licencias">
          <p>
            Los datos salen sobre todo del Portal de Datos Abiertos de la Comunidad de Madrid: hoy, <CmCount /> de sus
            conjuntos de datos. La lista completa, con la versión, la licencia y el enlace de cada uno, está en{" "}
            <code>GET /api/v1/datasets</code> (más abajo).
          </p>
          <ul className={styles.list}>
            <li>
              <strong>Código:</strong> <a href={repoFile("LICENSE")}>Apache-2.0</a>.
            </li>
            <li>
              <strong>Documentación y catálogo de datos:</strong> <a href={repoFile("docs/LICENSE")}>CC BY 4.0</a>.
            </li>
            <li>
              <strong>Cada conjunto de datos conserva su licencia:</strong>
              <ul className={styles.list}>
                <li>Comunidad de Madrid y Ayuntamiento de Madrid: CC BY 4.0.</li>
                <li>Consorcio Regional de Transportes de Madrid: su licencia de datos abiertos («Powered by CRTM»).</li>
                <li>
                  OpenStreetMap: ODbL. También el anillo de la M-40 que delimita el piloto para inversores, que es un derivado
                  de OpenStreetMap.
                </li>
                <li>CartoCiudad (Instituto Geográfico Nacional): CC BY 4.0 scne.es.</li>
                <li>
                  Ministerio de Sanidad, Ministerio de Vivienda y Agencia Tributaria: reutilización citando la fuente y la
                  fecha de su última actualización.
                </li>
              </ul>
            </li>
          </ul>
          <p>
            Cada conjunto de datos de una respuesta (<code>datasets</code>) trae su <code>license</code>, su{" "}
            <code>url</code> y su <code>attribution_text</code>: el texto con el que pide que lo cites. Si reutilizas las
            cifras, cítalo.
          </p>
          <p>
            <a href={repoFolder("data/catalog/datasets")}>La ficha de cada conjunto de datos, en el repositorio</a>
          </p>
        </Section>

        <Section id="funciona-hoy" badge={TEXT.works}>
          <p>
            Estas rutas están en producción. {TEXT.verified} Copia el ejemplo y pégalo en un terminal. Las respuestas son
            JSON; con <code>jq</code> puedes quedarte con una parte, por ejemplo <code>{"| jq .meta"}</code>.
          </p>
          {API_GROUPS.map((group) => (
            <section key={group.id} className={styles.group} aria-labelledby={`grupo-${group.id}`}>
              <h3 id={`grupo-${group.id}`} className={styles.subhead}>
                {group.title}
              </h3>
              {group.examples.map((example) => (
                <Example key={example.id} example={example} />
              ))}
            </section>
          ))}
        </Section>

        <Section id="mcp" badge={TEXT.local}>
          <p>
            El MCP (Model Context Protocol) deja que un asistente de IA, como Claude Desktop o Claude Code, pregunte a Vida
            Fácil lo mismo que la API y reciba las mismas cifras y las mismas fuentes. Sus herramientas son de solo lectura,
            llaman a las mismas funciones que la API y nunca ejecutan SQL.
          </p>
          <p className={styles.notice}>
            <strong>Hoy funciona en tu ordenador, no en remoto.</strong> El servidor se arranca en local y habla con tu
            asistente por stdio. Necesita una copia del repositorio y una base de datos Postgres con los datos cargados.
          </p>
          <h3 className={styles.subhead}>Sus {MCP_TOOLS.length} herramientas</h3>
          <ul className={styles.tools}>
            {MCP_TOOLS.map((tool) => (
              <li key={tool.name}>
                <code>{tool.name}</code>: {tool.text}
                {tool.isNew && <span className={styles.badge}>{TEXT.isNew}</span>}
              </li>
            ))}
          </ul>
          <h3 className={styles.subhead}>Cómo conectarlo</h3>
          <ol className={styles.steps}>
            <li>
              <p>
                Necesitas git, Docker y uv, con Python 3.12 (<a href="https://docs.astral.sh/uv/">cómo instalar uv</a>).
                Clona el repositorio y carga los datos. La carga tarda: descarga los datos abiertos, los valida y calcula
                los indicadores.
              </p>
              <CodeBlock code={MCP_SETUP} caption="Terminal" label="Clonar el repositorio y cargar los datos" />
            </li>
            <li>
              <p>
                <strong>Claude Code:</strong> cambia la ruta por la de tu copia del repositorio.
              </p>
              <CodeBlock code={MCP_CLAUDE_CODE} caption="Terminal" label="Añadir el MCP a Claude Code" />
            </li>
            <li>
              <p>
                <strong>Claude Desktop:</strong> añádelo a <code>claude_desktop_config.json</code>, con la ruta completa
                de tu copia. <code>uv</code> tiene que estar en el PATH de la aplicación (o pon su ruta completa).
              </p>
              <CodeBlock code={MCP_CLAUDE_DESKTOP} caption="claude_desktop_config.json" label="Añadir el MCP a Claude Desktop" />
            </li>
          </ol>
          <p>
            <code>DATABASE_URL</code> apunta a la base que crea <code>make dev</code>, con el usuario y la contraseña de{" "}
            <code>.env</code>. Después, pregúntale por ejemplo «¿Qué le falta a Chamartín?» o «¿Sale una promoción de
            1.000 m² en Pinar del Rey con el suelo a 3.200 € el m² edificable?».
          </p>
        </Section>

        <Section id="planteado" badge={TEXT.planned}>
          <p>Ideas en las que trabajamos. Hoy no existen, así que no cuentes con ellas todavía. No damos fechas.</p>
          <ul className={styles.planned}>
            {PLANNED.map((item) => (
              <li key={item.title}>
                <p className={styles.plannedTitle}>
                  <strong>{item.title}</strong> <span className={styles.badgeQuiet}>{TEXT.planned}</span>
                </p>
                <p>{item.text}</p>
              </li>
            ))}
          </ul>
        </Section>

        <Section id="uso-justo">
          <p>La API es gratis y la mantiene un proyecto pequeño. Para que siga así, te pedimos:</p>
          <ul className={styles.list}>
            <li>
              Guarda en caché lo que pidas: los datos cambian pocas veces, y <code>meta.data_version</code> te dice cuándo.
            </li>
            <li>No la llames en bucle ni pidas lo mismo una y otra vez.</li>
            <li>
              Si vas a hacer muchas peticiones, cuéntanoslo antes en <a href={`${REPO_URL}/issues`}>el repositorio</a>.
            </li>
          </ul>
          <p>Gracias.</p>
        </Section>

        <Section id="mas">
          <ul className={styles.list}>
            <li>
              <a href={REPO_URL}>El código, en GitHub</a> (Apache-2.0).
            </li>
            <li>
              <a href={repoFile("docs/04_technical_architecture/31_public_api_routes.md")}>Las rutas y sus contratos</a>, con
              lo que la web puede dar por hecho de cada respuesta.
            </li>
            <li>
              <a href={repoFile("docs/04_technical_architecture/32_mcp_server.md")}>El servidor MCP</a>: herramientas,
              pruebas y tiempos.
            </li>
            <li>
              <a href={repoFolder("data/schemas/api")}>Los JSON Schema de cada respuesta</a>, para generar tus tipos.
            </li>
          </ul>
        </Section>
      </div>
      <SiteFooter />
    </div>
  );
}

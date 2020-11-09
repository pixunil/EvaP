import { Page, ElementHandle } from "puppeteer";

import { pageHandler } from "utils/page";
import "utils/matchers";

interface TextResultsPublishConfirmationElements {
    top: ElementHandle,
    bottom: ElementHandle,
    bottomCard: ElementHandle,
}

async function query(page: Page): Promise<TextResultsPublishConfirmationElements> {
    return {
        top: (await page.$("#text_results_publish_confirmation_top"))!,
        bottom: (await page.$("#text_results_publish_confirmation_bottom"))!,
        bottomCard: (await page.$("#bottom_text_results_publish_confirmation_card"))!,
    };
}

async function queryClosest(element: ElementHandle, selector: string): Promise<ElementHandle> {
    return element.evaluateHandle((element, selector) => {
        return element.closest(selector);
    }, selector).then(handle => handle.asElement()!);
}

async function queryParent(element: ElementHandle): Promise<ElementHandle> {
    return element.evaluateHandle(element => {
        return element.parentElement;
    }).then(handle => handle.asElement()!);
}

test("checking top confirm checkbox checks and hides bottom", pageHandler(
    "student/vote/1/with_textanswer_publish_confirmation.html",
    async page => {
        const elements = await query(page);
        await elements.top.click();

        await expect(elements.bottom).toBeChecked();
        await expect(elements.bottomCard).toHaveClass("d-none");
    },
));

test("checking bottom confirm checkbox check top but keeps bottom visible", pageHandler(
    "student/vote/1/with_textanswer_publish_confirmation.html",
    async page => {
        const elements = await query(page);
        await elements.bottom.click();

        await expect(elements.top).toBeChecked();
        await expect(elements.bottomCard).not.toHaveClass("d-none");
    },
));

test("resolving submit errors clears warning", pageHandler(
    "student/vote/1/submit_errors.html",
    async page => {
        const checkbox = (await page.$(".choice-error input[type=radio][value='3']"))!;
        await checkbox.click();
        const row = await queryClosest(checkbox, ".row");
        expect(await row.$$(".choice-error")).toHaveLength(0);
    },
));

test("skip contributor", pageHandler(
    "student/vote/1/normal.html",
    async page => {
        const voteArea = (await page.$(".card .collapse"))!;
        const button = (await queryClosest(voteArea, ".card").then(card => card.$("button")))!;
        await button.click();
        for (const checkbox of await voteArea.$$("input[type=radio]:not([value='6'])")) {
            await expect(checkbox).not.toBeChecked();
            await expect(await queryParent(checkbox)).not.toHaveClass("active");
        }
        for (const checkbox of await voteArea.$$("input[type=radio][value='6']")) {
            await expect(checkbox).toBeChecked();
            await expect(await queryParent(checkbox)).toHaveClass("active");
        }
        await expect(voteArea).toHaveClass("collapsing");
    },
));

test("skipping contributor clears warning", pageHandler(
    "student/vote/1/submit_errors.html",
    async page => {
        const voteArea = (await page.$(".card .collapse"))!;
        const button = (await queryClosest(voteArea, ".card").then(card => card.$("button")))!;
        await button.click();
        await expect(await voteArea.$$(".choice-error")).toHaveLength(0);
    },
));
